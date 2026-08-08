# Box name

Copy this README into each box directory and keep this structure for examples and submissions. Replace every placeholder before publishing.

| Field | Value |
| --- | --- |
| Box ID | `<id from box.yaml>` |
| Competition ID | `<competitionId from box.yaml>` |
| Difficulty | `<easy \| medium \| hard \| insane>` |
| Run type | `<container \| vm \| network>` |
| Target OS | `<linux \| windows \| mixed>` |
| Categories | `<web, privilege-escalation, ...> `|

> Replace all placeholders before submitting the box.


## Overview

Describe the challenge scenario, the exposed attack surface, and what the agent is expected to achieve.


## Vulnerability

Explain the main vulnerability or weakness the challenge is built around. Include relevant CWE references where useful.


## Intended solve path

Outline the expected path from initial discovery to the final objective. Include any required exploitation, privilege escalation, lateral movement, or pivoting.

1. `<Discovery or initial access>`
2. `<Exploitation>`
3. `<Privilege escalation or pivot, if applicable>`
4. `<Final objective>`


## Objective & flags

Document each objective, including where it is located and what level of access is required.

- **Objective:** `<objective name>`
- **Host:** `<host>`
- **Gating:** `<user | root | service-user | administrator | system | domain-admin>`
- **Runtime variable:** `DESTRIER_FLAG_<HOST>_<GATING>`
- **Proof point:** `<where the flag becomes accessible>`

Do not commit real flags. Destrier injects fresh values at runtime. If a checked-in file requires a placeholder, use `__DESTRIER_FLAG_<HOST>_<GATING>__` instead.


> Replace the placeholder during provisioning or startup.


## Notes

Add anything reviewers should know that is not already covered above, such as difficulty considerations, assumptions, build requirements, unusual behaviour, or implementation details.