# Building this VM

A VM box is authored like a container box: you write **provisioning steps**, not
a disk image. Packer boots the installer, runs the steps in order, and snapshots
the result to qcow2.

```
target/host/
  box.pkr.hcl              the build definition — read this first
  http/autounattend.xml    answers the Windows installer + enables WinRM
  files/                   anything to copy onto the box (installers, configs, web roots)
  scripts/
    00-base.ps1            roles, features, accounts
    10-registry.ps1        registry changes
    20-vulnerable.ps1      the CVE / the vulnerability itself
    30-flag-hook.ps1       per-run flag planter
    99-generalize.ps1      cleanup + sysprep
```

"Ten files, ten registry keys, ten config changes" are not ten problems — they
are lines in `files/` and `scripts/`. Add to the list; the shape does not change.

## Getting the ISO

Use Microsoft's **free 180-day evaluation ISO** of Windows Server. It costs
nothing, it is what labs normally do, and it avoids per-hour licensed cloud
images. Re-bake when the evaluation lapses.

```bash
packer init .
packer build \
  -var "box_id=my-box" \
  -var "iso_url=/path/to/windows-server-2022-eval.iso" \
  -var "iso_checksum=sha256:..." .
```

Output lands in `output/my-box.qcow2`.

## Building a CVE box

The only step that differs from any other box is `20-vulnerable.ps1`:

1. **Pin the affected version.** Never `latest` — a rebuild would silently patch
   your box and it would look fine while being unsolvable.
2. **Name the CVE in the script.** A reviewer, and future you, needs to know
   what this box is.
3. **Make it reachable**, and make the port match `box.yaml`. The hop in front
   of this host only listens on declared ports, so a service on an undeclared
   one is invisible to the agent.
4. **Prove it.** Your `solver/` must exploit it end to end. A box whose solver
   does not run is not a box.

## Domain controllers

Install the role at build time; **promote at first boot**, not in Packer.
Microsoft does not support sysprepping a promoted DC — doing it corrupts the
domain. Promoting per run is also better: the domain name, DSRM password and
account passwords all derive from the run's seed, so they rotate the way flags
do instead of being identical in every run.

Budget for it: a Windows build is 20–40 minutes, and DC promotion adds two
reboots to first boot.

## The iteration loop (read this before your first build)

A 30-minute build is a miserable edit-compile-run cycle. Do not develop that
way:

1. Build **once** with `packer build -on-error=ask`. On failure Packer leaves
   the machine up.
2. Develop against that live machine — RDP or WinRM in, run your script, fix,
   run again. Seconds per attempt instead of half an hour.
3. Only when a script is right, fold it back into `scripts/` and do a clean
   rebuild to prove it works from zero.

The clean rebuild matters: a box that only works because of something you did
by hand is a box that will not come up in a run.

## Flags

Never bake a flag into the image. `30-flag-hook.ps1` installs a boot-time task
that derives them from the run's seed, so a flag captured in one run is wrong in
the next. That is what makes a correct submission proof of a solve rather than
proof of a good memory.
