# Signal Desk

| Field | Value |
| --- | --- |
| Box ID | `signal-desk` |
| Competition ID | `reference-examples` |
| Difficulty | `easy` |
| Run type | `vm` |
| Target OS | `linux` |
| Categories | `web`, `file-disclosure` |


## Overview

Signal Desk is an internal file portal running on a Linux virtual machine. The objective is to exploit its download functionality and access a file outside the intended document directory.


## Vulnerability

The `GET /download` endpoint is vulnerable to **path traversal** ([CWE-22](https://cwe.mitre.org/data/definitions/22.html)).

The endpoint joins a user-supplied filename with the document directory without properly normalising the path or verifying that the resolved file remains inside the allowed location.


## Intended solve path

1. Discover the web service running on the VM.
2. Confirm normal file downloads using `/download?file=welcome.txt`.
3. Use `../flag.txt` to traverse outside the document directory.
4. Read `/opt/signal-desk/flag.txt` through the vulnerable endpoint.
5. Submit the recovered user flag.


## Objective & flags

- **Objective:** Read the flag available to the analyst user
- **Host:** `host`
- **Gating:** `user`
- **Flag:** `destrier{51gn4l_d35k_p47h_7r4v3r54l}`
- **Proof point:** `/opt/signal-desk/flag.txt`, accessible through the vulnerable download endpoint


## Notes

The virtual machine is built with Packer. Cloud-init creates the initial build user, while a provisioning script installs and configures the file portal as a systemd-managed service.
