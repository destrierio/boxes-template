#!/usr/bin/env python3
"""
Validate contributor boxes.

Validates every `box.yaml` in the repository except the repo's reference
directories (`example-box/`, `network-example/`, and `templates/`). Any other
directory is treated as a contributor box, regardless of its name.

For each box, validates that:
  1. `box.yaml` conforms to `schemas/box.schema.json`.
  2. Cross-references are valid (for example, `flag.host`,
     `entrypoint.network`, and host networks).
  3. Required directories exist (`target/`, `solver/`, and each host's build
     path).

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
 
    # schema
    for e in sorted(VALIDATOR.iter_errors(doc), key=lambda e: list(e.path)):
        loc = "/".join(str(x) for x in e.path) or "(root)"
        errors.append(f"schema: {loc}: {e.message}")
    if errors:
        return errors 
 
    # cross-references
    net_names = {n["name"] for n in doc["networks"]}
    host_names = [h["name"] for h in doc["hosts"]]
    if len(host_names) != len(set(host_names)):
        errors.append("hosts: duplicate host names")
    for f in doc["flags"]:
        if f["host"] not in host_names:
            errors.append(f"flags: host '{f['host']}' is not a defined host")
    if doc["entrypoint"]["network"] not in net_names:
        errors.append(f"entrypoint.network '{doc['entrypoint']['network']}' is not a defined network")
    for h in doc["hosts"]:
        for n in h["networks"]:
            if n not in net_names:
                errors.append(f"host '{h['name']}' references undefined network '{n}'")
 
    kinds = [h["kind"] for h in doc["hosts"]]
    rt = doc["runType"]
    if rt == "container" and not (len(doc["hosts"]) == 1 and kinds[0] == "container"):
        errors.append("runType 'container' requires exactly one host of kind container")
    elif rt == "vm" and not (len(doc["hosts"]) == 1 and kinds[0] == "vm"):
        errors.append("runType 'vm' requires exactly one host of kind vm")
    elif rt == "network" and len(doc["hosts"]) < 2:
        errors.append("runType 'network' requires at least two hosts")
 
    # structure
    if not (box_dir / "target").is_dir():
        errors.append("missing target/ directory")
    if not (box_dir / "solver").is_dir():
        errors.append("missing solver/ directory")
    for h in doc["hosts"]:
        if not (box_dir / h["build"]).is_dir():
            errors.append(f"host '{h['name']}': build path '{h['build']}' does not exist")
 
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
