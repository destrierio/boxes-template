# Bulletin

| Field | Value |
| --- | --- |
| Box ID | `bulletin` |
| Competition ID | `reference-examples` |
| Difficulty | `easy` |
| Run type | `container` |
| Target OS | `linux` |
| Categories | `web` |


## Overview

Bulletin is an internal announcement service with a template preview feature. The objective is to exploit the preview functionality and retrieve the flag available to the web service user.


## Vulnerability

The `POST /preview` endpoint is vulnerable to **server-side template injection (SSTI)** through Jinja2's `render_template_string` ([CWE-1336](https://cwe.mitre.org/data/definitions/1336.html)). 

A denylist blocks common command-execution techniques, but the template environment still exposes a path to arbitrary file reads.


## Intended solve path

1. Discover the `/preview` endpoint.
2. Confirm template injection using `{{7*7}}`.
3. Identify that common command-execution payloads are blocked.
4. Use the available Jinja2 environment to read `/flag.txt`.
5. Submit the recovered service-user flag.


## Objective & flags

Document each objective, including where it is located and what level of access is required.

- **Objective:** Read the flag as the web service user
- **Host:** `app`
- **Gating:** `service-user`
- **Runtime variable:** `DESTRIER_FLAG_APP_SERVICE_USER`
- **Proof point:** `/flag.txt`, readable by the `web` service user


## Notes

The denylist is intentionally incomplete. The intended solution is to inspect and reason about the available template environment to achieve a file read rather than relying on a standard SSTI command-execution payload.