# Bulletin

A complete reference box showing how a finished box fits together: the manifest (`box.yaml`), the target (`target/`), and the reference solver (`solver/`).

- **Box ID:** bulletin
- **Difficulty:** medium
- **Run type:** container
- **Target OS:** linux
- **Category:** web


## Overview

Bulletin is an internal announcement service with a preview feature. User-supplied templates are rendered directly by the server before publication.


## Vulnerability

`POST /preview` is vulnerable to server-side template injection (SSTI, CWE-1336). User input is passed directly to Jinja2 via `render_template_string`. A simple denylist blocks common command-execution gadgets (`popen`, `system`, `subprocess`, `__import__`), preventing a straightforward RCE payload.


## Intended solve path

1. Discover the `/preview` endpoint.
2. Confirm SSTI by evaluating `{{7*7}}`.
3. Observe that a command-execution payload is blocked.
4. Read the flag directly through the template engine using a file-read gadget.
5. Retrieve `/flag.txt`.


## Objective & flags

- **Objective:** Read the flag as the `service-user`.
- **Flag:** One flag on host `app`, gated to `service-user` and generated for every run.


## Notes

The denylist intentionally blocks common command-execution gadgets without preventing file reads. The intended solution is to reason about the template environment rather than rely on a standard SSTI RCE payload.