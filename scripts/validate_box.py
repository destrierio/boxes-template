#!/usr/bin/env python3
"""
Validate Destrier boxes.

Validates the shipped examples and every contributor `box.yaml`. Starter
manifests under `templates/` are excluded because they are intentionally
incomplete until copied into a box directory.

For each box, checks that:

1. The manifest follows the required format.
2. All references within the manifest are valid and unambiguous.
3. The run type is compatible with the defined hosts.
4. Build inputs exist, use the expected format, and stay inside the box.
5. Network settings and host IP addresses are valid.
6. The required files and directories are present.
7. Static flag values are unique.
8. The competition and box identity route to a unique storage namespace.

Exits with status 0 if all checks pass, otherwise 1.
"""

import ipaddress
import json
import sys
from collections import Counter
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parent.parent
SCHEMA = json.loads((ROOT / "schemas" / "box.schema.json").read_text())
VALIDATOR = Draft202012Validator(SCHEMA)

RESERVED = {"templates"}


def find_boxes(roots: list[Path] | None = None):
    if roots:
        for root in roots:
            if root.is_file():
                yield root.resolve()
            else:
                yield from sorted(p.resolve() for p in root.rglob("box.yaml"))
        return
    for path in sorted(ROOT.rglob("box.yaml")):
        relative_path = path.relative_to(ROOT)
        if relative_path.parts and relative_path.parts[0] in RESERVED:
            continue
        yield path


def duplicates(values: list[str]) -> list[str]:
    return sorted(value for value, count in Counter(values).items() if count > 1)


def box_path(box_dir: Path, raw_path: str, field: str, errors: list[str]) -> Path | None:
    candidate = Path(raw_path)
    if candidate.is_absolute():
        errors.append(f"{field} must be relative to the box directory")
        return None

    try:
        box_root = box_dir.resolve()
        resolved = (box_dir / candidate).resolve()
    except (OSError, RuntimeError, ValueError) as error:
        errors.append(f"cannot resolve {field}: {error}")
        return None
    try:
        resolved.relative_to(box_root)
    except ValueError:
        errors.append(f"{field} must stay inside the box directory")
        return None
    return resolved


def has_packer_definition(source_dir: Path) -> bool:
    try:
        candidates = (*source_dir.glob("*.pkr.hcl"), *source_dir.glob("*.pkr.json"))
        return any(candidate.is_file() for candidate in candidates)
    except OSError:
        return False


def check(box_yaml: Path) -> list[str]:
    errors: list[str] = []
    box_dir = box_yaml.parent

    try:
        manifest_text = box_yaml.read_text()
    except (OSError, UnicodeError) as error:
        return [f"cannot read manifest: {error}"]

    try:
        doc = yaml.safe_load(manifest_text)
    except yaml.YAMLError as error:
        return [f"invalid YAML: {error}"]

    schema_errors = sorted(
        VALIDATOR.iter_errors(doc),
        key=lambda error: tuple(str(part) for part in error.absolute_path),
    )
    for error in schema_errors:
        location = "/".join(str(part) for part in error.absolute_path) or "(root)"
        errors.append(f"schema: {location}: {error.message}")
    if errors:
        return errors

    network_names = [network["name"] for network in doc["networks"]]
    network_cidrs = [network["cidr"] for network in doc["networks"]]
    for name in duplicates(network_names):
        errors.append(f"networks: duplicate network name '{name}'")
    for cidr in duplicates(network_cidrs):
        errors.append(f"networks: duplicate network CIDR '{cidr}'")

    net_cidr: dict[str, str] = {}
    for network in doc["networks"]:
        net_cidr.setdefault(network["name"], network["cidr"])

    host_names = [host["name"] for host in doc["hosts"]]
    for name in duplicates(host_names):
        errors.append(f"hosts: duplicate host name '{name}'")

    for flag in doc["flags"]:
        if flag["host"] not in host_names:
            errors.append(f"flags: host '{flag['host']}' is not a defined host")

    # Flags are static, so two flags sharing a value means capturing one hands
    # over the other -- across hosts, and across gating levels that are supposed
    # to represent different work.
    flag_values = [flag["value"] for flag in doc["flags"]]
    for value in duplicates(flag_values):
        errors.append(f"flags: duplicate flag value '{value}'")

    if doc["entrypoint"]["network"] not in net_cidr:
        errors.append(
            f"entrypoint.network '{doc['entrypoint']['network']}' is not a defined network"
        )

    kinds = [host["kind"] for host in doc["hosts"]]
    run_type = doc["runType"]
    if run_type == "container" and not (
        len(doc["hosts"]) == 1 and kinds[0] == "container"
    ):
        errors.append("runType 'container' requires exactly one host of kind container")
    elif run_type == "vm" and not (len(doc["hosts"]) == 1 and kinds[0] == "vm"):
        errors.append("runType 'vm' requires exactly one host of kind vm")
    elif run_type == "network" and len(doc["hosts"]) < 2:
        errors.append("runType 'network' requires at least two hosts")

    used_ips: dict[str, set[str]] = {}
    for host in doc["hosts"]:
        name = host["name"]
        kind = host["kind"]
        role = host.get("role")
        source = host["build"].get("source")
        image = host["build"].get("image")
        image_path = image if isinstance(image, str) else (image or {}).get("path")

        if role == "domain-controller":
            if kind != "vm" or host.get("os") != "windows":
                errors.append(
                    f"host '{name}': a domain-controller must be a Windows VM"
                )
            if not image:
                errors.append(
                    f"host '{name}': a domain-controller must provide build.image"
                )
            if source:
                errors.append(
                    f"host '{name}': a domain-controller cannot provide build.source"
                )
        else:
            if source and image:
                errors.append(
                    f"host '{name}': declare build.source or build.image, not both"
                )
            elif not source and not image:
                errors.append(f"host '{name}': build.source or build.image is required")
            elif image and kind != "vm":
                errors.append(
                    f"host '{name}': only a vm can ship a prebuilt disk image"
                )

        if source:
            source_dir = box_path(
                box_dir, source, f"host '{name}': build.source", errors
            )
            if source_dir is not None:
                if not source_dir.is_dir():
                    errors.append(
                        f"host '{name}': build source '{source}' does not exist"
                    )
                elif kind == "container" and not (source_dir / "Dockerfile").is_file():
                    errors.append(
                        f"host '{name}': container build source '{source}' has no Dockerfile"
                    )
                elif kind == "vm" and not has_packer_definition(source_dir):
                    errors.append(
                        f"host '{name}': VM build source '{source}' has no Packer definition"
                    )

        if image_path:
            resolved_image = box_path(
                box_dir, image_path, f"host '{name}': build.image", errors
            )
            # An already-pushed image may legitimately have been cleaned up: the
            # platform holds the bytes by digest, the path is only a breadcrumb.
            if (
                resolved_image is not None
                and isinstance(image, str)
                and not resolved_image.is_file()
            ):
                errors.append(f"host '{name}': build image '{image_path}' does not exist")

        attached_networks: set[str] = set()
        for attachment in host["networks"]:
            network_name = attachment["name"]
            ip_text = attachment["ip"]
            if network_name in attached_networks:
                errors.append(
                    f"host '{name}': network '{network_name}' is attached more than once"
                )
            attached_networks.add(network_name)

            if network_name not in net_cidr:
                errors.append(
                    f"host '{name}' references undefined network '{network_name}'"
                )
                continue

            try:
                address = ipaddress.ip_address(ip_text)
                network = ipaddress.ip_network(net_cidr[network_name], strict=True)
            except ValueError as error:
                errors.append(f"host '{name}': invalid network address: {error}")
                continue

            if address not in network:
                errors.append(
                    f"host '{name}': IP {ip_text} is not inside network "
                    f"'{network_name}' ({network})"
                )
            if address in (network.network_address, network.broadcast_address):
                errors.append(
                    f"host '{name}': IP {ip_text} cannot be a network or broadcast address"
                )

            seen = used_ips.setdefault(network_name, set())
            if ip_text in seen:
                errors.append(
                    f"network '{network_name}': IP {ip_text} is used by more than one host"
                )
            seen.add(ip_text)

        healthcheck = host.get("healthcheck")
        if healthcheck:
            port = int(healthcheck.split(":", 1)[1].split("/", 1)[0])
            if not 1 <= port <= 65535:
                errors.append(
                    f"host '{name}': healthcheck port must be between 1 and 65535"
                )

    if not (box_dir / "solver").is_dir():
        errors.append("missing solver/ directory")

    return errors


def manifest_identity(box_yaml: Path) -> tuple[str, str]:
    doc = yaml.safe_load(box_yaml.read_text())
    return doc["competitionId"], doc["id"]


def main(argv: list[str] | None = None) -> int:
    roots = [Path(a) for a in (argv if argv is not None else sys.argv[1:])]
    for root in roots:
        if not root.exists():
            print(f"no such path: {root}")
            return 1
    boxes = list(find_boxes(roots))
    if not boxes:
        print("no box found to validate")
        return 1

    box_errors: dict[Path, list[str]] = {}
    valid_identities: list[tuple[Path, str, str]] = []
    for box in boxes:
        errors = check(box)
        box_errors[box] = errors
        if not errors:
            competition_id, box_id = manifest_identity(box)
            valid_identities.append((box, competition_id, box_id))

    seen_identities: dict[str, Path] = {}
    for box, competition_id, box_id in valid_identities:
        identity = f"{competition_id}/{box_id}"
        if identity in seen_identities:
            original = seen_identities[identity]
            box_errors[box].append(
                f"identity: duplicate competitionId/id '{identity}' also used by {original}"
            )
        else:
            seen_identities[identity] = box

    failed = 0
    for box in boxes:
        try:
            relative_path = box.relative_to(ROOT)
        except ValueError:
            relative_path = box
        errors = box_errors[box]
        if errors:
            failed += 1
            print(f"FAIL  {relative_path}")
            for error in errors:
                print(f"        - {error}")
        else:
            print(f"OK    {relative_path}")

    if failed:
        print(f"\n{failed} box(es) failed validation")
        return 1

    print(f"\nall {len(boxes)} box(es) passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
