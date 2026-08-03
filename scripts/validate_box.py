#!/usr/bin/env python3
"""
Validate contributor boxes.

Validates every `box.yaml` in the repository except the templates's reference
directories (`example-box/`, `network-example/`, and `templates/`). Any other
directory is treated as a contributor box, regardless of its name.

For each box, validates that:
  1. The manifest matches the schema.
  2. All manifest cross-references are valid.
  3. The run type matches the host definitions.
  4. Each host uses the correct build method.
  5. Networks and host IPs are valid.
  6. The required directory structure is present.

Exits with status 0 if all checks pass, otherwise 1.
"""
import json
import sys
from pathlib import Path
 
import yaml
from jsonschema import Draft202012Validator
 
ROOT = Path(__file__).resolve().parent.parent
SCHEMA = json.loads((ROOT / "schemas" / "box.schema.json").read_text())
VALIDATOR = Draft202012Validator(SCHEMA)
 
RESERVED = {"example-box", "network-example", "templates"}
 
 
def find_boxes():
    for p in ROOT.rglob("box.yaml"):
        parts = p.relative_to(ROOT).parts
        if any(part in RESERVED for part in parts):
            continue
        yield p
 
 
def check(box_yaml: Path) -> list[str]:
    errors: list[str] = []
    box_dir = box_yaml.parent
    try:
        doc = yaml.safe_load(box_yaml.read_text())
    except yaml.YAMLError as e:
        return [f"invalid YAML: {e}"]
 
    for e in sorted(VALIDATOR.iter_errors(doc), key=lambda e: list(e.path)):
        loc = "/".join(str(x) for x in e.path) or "(root)"
        errors.append(f"schema: {loc}: {e.message}")
    if errors:
        return errors 
 
    net_cidr = {n["name"]: n["cidr"] for n in doc["networks"]}
    host_names = [h["name"] for h in doc["hosts"]]
 
    # validate cross-references
    if len(host_names) != len(set(host_names)):
        errors.append("hosts: duplicate host names")
    for f in doc["flags"]:
        if f["host"] not in host_names:
            errors.append(f"flags: host '{f['host']}' is not a defined host")
    if doc["entrypoint"]["network"] not in net_cidr:
        errors.append(f"entrypoint.network '{doc['entrypoint']['network']}' is not a defined network")
 
    # ensure the declared run type matches teh host layout
    kinds = [h["kind"] for h in doc["hosts"]]
    rt = doc["runType"]
    if rt == "container" and not (len(doc["hosts"]) == 1 and kinds[0] == "container"):
        errors.append("runType 'container' requires exactly one host of kind container")
    elif rt == "vm" and not (len(doc["hosts"]) == 1 and kinds[0] == "vm"):
        errors.append("runType 'vm' requires exactly one host of kind vm")
    elif rt == "network" and len(doc["hosts"]) < 2:
        errors.append("runType 'network' requires at least two hosts")
 
    # validate each host's build method, role, networking, and structure
    used_ips: dict[str, set] = {}
    for h in doc["hosts"]:
        name, kind = h["name"], h["kind"]
        role = h.get("role")
        btype = h["build"]["type"]
 
        # ensure the build method is valid for this host
        if kind == "container":
            if btype != "dockerfile":
                errors.append(f"host '{name}': a container must build from source (build.type: dockerfile)")
            if role:
                errors.append(f"host '{name}': a container cannot have a role")
        elif kind == "vm":
            if role == "domain-controller":
                if btype != "image":
                    errors.append(f"host '{name}': a domain-controller must ship a prebuilt image (build.type: image)")
            else:
                if btype != "packer":
                    errors.append(f"host '{name}': a vm must build from source (build.type: packer)")
        if btype == "image" and role != "domain-controller":
            errors.append(f"host '{name}': build.type 'image' is only allowed for a domain-controller")
 
        # validate the build definition and require files
        if btype in ("dockerfile", "packer"):
            path = h["build"].get("path")
            if not path:
                errors.append(f"host '{name}': build.path is required for a source build")
            elif not (box_dir / path).is_dir():
                errors.append(f"host '{name}': build path '{path}' does not exist")
        elif btype == "image":
            if not h["build"].get("image"):
                errors.append(f"host '{name}': build.image (filename) is required for an image build")
 
        # validate host IP assignments
        for attach in h["networks"]:
            nname, ip = attach["name"], attach["ip"]
            if nname not in net_cidr:
                errors.append(f"host '{name}' references undefined network '{nname}'")
                continue
            ip_octets = ip.split(".")
            cidr_third = net_cidr[nname].split(".")[2]
            if ip_octets[2] != cidr_third:
                errors.append(f"host '{name}': IP {ip} is not inside network '{nname}' ({net_cidr[nname]})")
            if ip_octets[3] in ("0", "255"):
                errors.append(f"host '{name}': IP {ip} cannot be a network or broadcast address")
            seen = used_ips.setdefault(nname, set())
            if ip in seen:
                errors.append(f"network '{nname}': IP {ip} is used by more than one host")
            seen.add(ip)
 
    if not (box_dir / "solver").is_dir():
        errors.append("missing solver/ directory")
 
    return errors
 
 
def main() -> int:
    boxes = list(find_boxes())
    if not boxes:
        print("no box found to validate (build your box in a folder of its own)")
        return 0
    failed = 0
    for box in boxes:
        rel = box.relative_to(ROOT)
        errs = check(box)
        if errs:
            failed += 1
            print(f"FAIL  {rel}")
            for e in errs:
                print(f"        - {e}")
        else:
            print(f"OK    {rel}")
    if failed:
        print(f"\n{failed} box(es) failed validation")
        return 1
    print(f"\nall {len(boxes)} box(es) passed")
    return 0
 
 
if __name__ == "__main__":
    sys.exit(main())
 