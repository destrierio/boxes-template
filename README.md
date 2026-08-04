# Destrier Box Template

Everything you need to build a challenge box for [Destrier](https://destrier.io).


## What's here

- `schemas/` — the JSON Schema your `box.yaml` is validated against.
- `scripts/` — the validation script CI runs on your box.
- `example-box/` — a complete reference box showing how everything fits together.
- `templates/` — Starter skeletons for `container`, `vm`, and `network` boxes.
- `your-box/` — Build your box here. Start by copying a template into this directory, then rename it to your box's ID before submitting.


## Build a box

1. Click **Use this template → Create a new repository** and set it to **Private**.
2. Copy a skeleton from `templates/` into `your-box/`, then rename the directory to your box's ID.
3. Build your box by following the guide at [docs.destrier.io](https://docs.destrier.io/contributing/overview).


## Validation

Every push runs a check that validates `your-box/box.yaml` against the schema and verifies your box's structure. Fix anything it reports before submitting.


## Submission

When your box is ready and the validation check passes:

1. Keep your repository **private**.
2. Add your Destrier reviewer as a collaborator with read access.
3. Share the repository link.

> Keep your repository private. It contains your reference exploit and other review-only material.


## How a host is built

A **virtual machine host** is built one of two ways, and the choice is yours:

- `build.type: packer` — built from a Packer template in your box, from source.
- `build.type: image` — a disk image you built however you like and uploaded with `boxr box push`.

A **container host** is always `build.type: dockerfile`.

A **domain controller** is the one host that must use `build.type: image`: building Active Directory from source for every evaluation is too slow, and the install is licensed and not reproducible in CI.

Uploading is one command from your box directory. There is no URL to request, no
filename to set and no digest to type:

```bash
boxr box push          # or `boxr box push <host>` for one host
```

It converts the disk to qcow2 if it is not already, fingerprints it, uploads
resumably, and writes `build.image` into `box.yaml` for you. Interrupt it and run
it again — it resumes. Run it after a rebuild and it uploads only what changed.

## Planting flags

**The platform mints a fresh flag for every run and tells your box what it is.
Your box plants it.** Nothing is baked into your image, and nothing is derived
from a shared seed — so a flag captured in one run is worthless in the next.

Each flag reaches exactly the host that holds it, named after its objective:

| variable                | when                                       |
| ----------------------- | ------------------------------------------ |
| `DESTRIER_FLAG_<ID>`    | always, one per flag on this host          |
| `DESTRIER_FLAG`         | only when this host holds exactly one flag |

The bare `DESTRIER_FLAG` is deliberately absent on a host with two flags, so a
box with a user flag and a root flag cannot plant one where the other belongs.

⚠️ **`<ID>` is derived from your `gating`, not chosen by you.** Take the
objective id, uppercase it, and replace every non-alphanumeric character with
`_`. The objective id is the `gating` on a single-host box, and
`<host>-<gating>` once the box has more than one host:

| box                   | flag                            | variable                          |
| --------------------- | ------------------------------- | --------------------------------- |
| one host              | `gating: root`                  | `DESTRIER_FLAG_ROOT`              |
| one host              | `gating: service-user`          | `DESTRIER_FLAG_SERVICE_USER`      |
| two hosts             | `host: dc`, `gating: root`      | `DESTRIER_FLAG_DC_ROOT`           |

Reading the wrong name **fails silently**: your fallback plants a fixed value,
the run scores zero on that objective, and nothing says why. If your host holds
exactly one flag, prefer the bare `DESTRIER_FLAG` — there is no name to get
wrong.

**Container hosts** get these as environment variables. Read them in your
entrypoint and write each flag where its gating says it should live.

**Virtual machine hosts** read them from QEMU's `fw_cfg`, because a booted disk
has no environment to inherit. The file is root-only, which is what keeps a user
flag out of reach of a user shell:

```sh
#!/bin/sh
# Run this once at boot, as root, before your services start.
FW=/sys/firmware/qemu_fw_cfg/by_name/opt/destrier/flags/raw
[ -r "$FW" ] || exit 0

while IFS='=' read -r key value; do
  [ -n "$key" ] && export "$key=$value"
done < "$FW"

# Plant each flag where its gating says it belongs, and set the ownership that
# makes that gating real.
printf '%s\n' "$DESTRIER_FLAG_ROOT" > /root/flag.txt
chmod 600 /root/flag.txt
chown root:root /root/flag.txt

printf '%s\n' "$DESTRIER_FLAG_USER" > /home/alice/flag.txt
chmod 640 /home/alice/flag.txt
chown alice:alice /home/alice/flag.txt
```

⚠️ **Your guest kernel must be 4.6 or newer** (`CONFIG_FW_CFG_SYSFS`). Debian,
Ubuntu, Alpine and RHEL all ship it enabled. If `/sys/firmware/qemu_fw_cfg` does
not exist in your image, the flags cannot reach it and every run of your box
will score zero — check for the directory before you submit.

Everything else — `box.yaml`, `solver/`, and all source-built hosts — is
submitted through your repository as usual.


## Learn more

See the full contributor guide at **[docs.destrier.io](https://docs.destrier.io/contributing/overview)**.