#!/usr/bin/env python3
"""
Schema tests for `box.yaml`.

`validate_box.py` checks the boxes that exist in the repository; it says nothing
about the cases that are *supposed* to fail. This file covers those, plus the
shipped manifests, so a change to the schema cannot quietly widen or break it.

Run: python3 scripts/test_schema.py
"""
import json
import sys
from copy import deepcopy
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parent.parent
SCHEMA = json.loads((ROOT / "schemas" / "box.schema.json").read_text())
VALIDATOR = Draft202012Validator(SCHEMA)

DIGEST = "sha256:" + "9f2c1e" + "0" * 58

IMAGE = {
    "artifact": DIGEST,
    "format": "qcow2",
    "sizeBytes": 42949672960,
    "builtFrom": "target/dc",
}

# A minimal manifest every case below varies one field of.
BASE = {
    "id": "example",
    "version": "1.0.0",
    "name": "Example",
    "authors": ["someone"],
    "runType": "vm",
    "category": ["web"],
    "difficulty": "easy",
    "objective": "Read the flag",
    "flags": [{"host": "host", "gating": "root"}],
    "entrypoint": {"network": "main"},
    "networks": [{"name": "main", "cidr": "10.10.0.0/24"}],
    "hosts": [
        {
            "name": "host",
            "kind": "vm",
            "build": {"type": "packer", "path": "target/host"},
            "networks": [{"name": "main", "ip": "10.10.0.10"}],
        }
    ],
    "limits": {"wallClockSeconds": 3600, "maxCostUsd": 8.0},
}


def with_build(build: dict, **host_fields) -> dict:
    """BASE with its single host's build replaced."""
    doc = deepcopy(BASE)
    doc["hosts"][0]["build"] = build
    doc["hosts"][0].update(host_fields)
    return doc


def errors(doc: dict) -> list[str]:
    return [e.message for e in VALIDATOR.iter_errors(doc)]


CASES: list[tuple[str, dict, bool]] = [
    # Source builds — the shape most boxes use, which must not move.
    ("packer source build", with_build({"type": "packer", "path": "target/host"}), True),
    ("dockerfile source build", with_build({"type": "dockerfile", "path": "target/app"}, kind="container"), True),
    # The uploaded-image branch.
    ("image build", with_build({"type": "image", "image": IMAGE}, role="domain-controller"), True),
    (
        "image without builtFrom",
        with_build({"type": "image", "image": {k: v for k, v in IMAGE.items() if k != "builtFrom"}}, role="domain-controller"),
        True,
    ),
    # ⚠️ The regression this file exists for. A filename here is how the format
    # started, and it is what a digest replaced: a name can be repointed at
    # different bytes, silently invalidating every score already recorded
    # against that box version.
    ("filename instead of a digest", with_build({"type": "image", "image": "dc.vmdk"}), False),
    ("bare hex, no sha256 prefix", with_build({"type": "image", "image": {**IMAGE, "artifact": "9f2c" + "0" * 60}}), False),
    ("uppercase digest", with_build({"type": "image", "image": {**IMAGE, "artifact": "sha256:" + "A" * 64}}), False),
    ("digest too short", with_build({"type": "image", "image": {**IMAGE, "artifact": "sha256:" + "a" * 63}}), False),
    # Format: qcow2 is what the platform boots. A vmdk uploading happily and
    # then failing at provision time is the failure this enum prevents.
    ("vmdk format", with_build({"type": "image", "image": {**IMAGE, "format": "vmdk"}}), False),
    ("raw format", with_build({"type": "image", "image": {**IMAGE, "format": "raw"}}), False),
    ("zero size", with_build({"type": "image", "image": {**IMAGE, "sizeBytes": 0}}), False),
    ("size as string", with_build({"type": "image", "image": {**IMAGE, "sizeBytes": "40GB"}}), False),
    ("unknown key in image", with_build({"type": "image", "image": {**IMAGE, "filename": "dc.vmdk"}}), False),
    ("missing artifact", with_build({"type": "image", "image": {k: v for k, v in IMAGE.items() if k != "artifact"}}), False),
    # The build discriminator itself.
    ("unknown build type", with_build({"type": "iso", "path": "target/host"}), False),
    ("build without a type", with_build({"path": "target/host"}), False),
]


def main() -> int:
    failed = 0

    for name, doc, should_pass in CASES:
        errs = errors(doc)
        ok = (not errs) if should_pass else bool(errs)
        if ok:
            print(f"OK    {name}")
        else:
            failed += 1
            want = "accept" if should_pass else "reject"
            print(f"FAIL  {name}: schema should {want} it")
            for e in errs[:3]:
                print(f"        - {e}")

    # Every manifest the repo ships must validate, templates included — an
    # author copies one of those and expects it to pass on the first run.
    for path in sorted(ROOT.rglob("box.yaml")):
        if ".git" in path.parts:
            continue
        errs = errors(yaml.safe_load(path.read_text()))
        rel = path.relative_to(ROOT)
        if errs:
            failed += 1
            print(f"FAIL  shipped manifest {rel}")
            for e in errs[:3]:
                print(f"        - {e}")
        else:
            print(f"OK    shipped manifest {rel}")

    if failed:
        print(f"\n{failed} case(s) failed")
        return 1
    print(f"\nall {len(CASES)} case(s) and every shipped manifest passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
