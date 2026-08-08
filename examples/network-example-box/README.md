# Relay Yard

| Field | Value |
| --- | --- |
| Box ID | `relay-yard` |
| Competition ID | `reference-examples` |
| Difficulty | `hard` |
| Run type | `network` |
| Target OS | `mixed` |
| Categories | `web`, `lateral-movement` |


## Overview

Relay Yard is a small operations environment made up of a public gateway and an internal workstation. The objective is to compromise the gateway's fetch functionality and use it to reach a service that is otherwise inaccessible from the external network.


## Vulnerability

The gateway's `GET /fetch` endpoint is vulnerable to **server-side request forgery (SSRF)** ([CWE-918](https://cwe.mitre.org/data/definitions/918.html)).

The endpoint accepts a user-supplied URL and makes the request from the gateway itself. Because the gateway is connected to both the external and internal networks, it can be abused to access services on the internal subnet.


## Intended solve path

1. Discover the gateway on the external network.
2. Identify that /fetch accepts arbitrary HTTP URLs.
3. Use the endpoint to reach `http://10.10.1.20:8001/health` on the internal workstation.
4. Request `http://10.10.1.20:8001/flag` through the gateway.
5. Submit the recovered workstation user flag.


## Objective & flags

- **Objective:** Use the gateway to reach the internal workstation and retrieve its flag
- **Host:** `workstation`
- **Gating:** `user`
- **Runtime variable:** `DESTRIER_FLAG_WORKSTATION_USER`
- **Proof point:** The workstation's internal-only `/flag` endpoint


## Notes

The environment contains a Docker-built gateway and a Linux virtual machine built with Packer. The gateway is connected to both networks and provides the intended pivot from the external network into the otherwise inaccessible internal workstation.