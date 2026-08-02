# Packer build for a VM box.
#
# A VM box is authored the way a container box is: you write provisioning
# steps, not a disk image. Packer boots the installer, runs what is below in
# order, and snapshots the result to qcow2.
#
#   packer init  .
#   packer build .
#
# Output: output/<box_id>.qcow2 — upload it to the box bucket and reference it
# from box.yaml. The platform boots it under QEMU-on-host.
#
# Windows note: build from Microsoft's free 180-day EVALUATION ISO. It is the
# standard way labs do this, it costs nothing, and it avoids per-hour licensed
# cloud images. Re-bake when the evaluation lapses.

packer {
  required_plugins {
    qemu = {
      source  = "github.com/hashicorp/qemu"
      version = "~> 1.1"
    }
  }
}

variable "box_id" {
  type    = string
  default = "your-box-id"
}

variable "iso_url" {
  type        = string
  description = "Path or URL to the installer ISO (Windows Server evaluation, or a Linux net-install)."
}

variable "iso_checksum" {
  type        = string
  description = "sha256:... — Packer refuses to build without it, which is the point."
}

# Credentials used ONLY during the build, so Packer can drive the machine.
# Anything the challenge depends on is set in scripts/, per run, from the seed.
variable "build_username" {
  type    = string
  default = "packer"
}

variable "build_password" {
  type      = string
  default   = "Packer!2026"
  sensitive = true
}

source "qemu" "box" {
  iso_url      = var.iso_url
  iso_checksum = var.iso_checksum

  # Legacy hardware, matching how the platform boots the image later. An image
  # built against virtio that is then booted with e1000/IDE will not find its
  # own disk.
  disk_interface = "ide"
  net_device     = "e1000"
  format         = "qcow2"
  disk_size      = "40G"
  memory         = 4096
  cpus           = 2
  accelerator    = "kvm"    # "hvf" on macOS, "tcg" if you have no accelerator

  headless         = true
  output_directory = "output"
  vm_name          = "${var.box_id}.qcow2"
  shutdown_timeout = "30m"

  # ── Windows ────────────────────────────────────────────────────────────
  # Packer drives Windows over WinRM. autounattend.xml answers the installer's
  # prompts and enables WinRM on first boot; without it the build hangs at the
  # first dialog with nobody to click it.
  communicator   = "winrm"
  winrm_username = var.build_username
  winrm_password = var.build_password
  winrm_timeout  = "4h"
  cd_files       = ["./http/autounattend.xml"]
  cd_label       = "cidata"
  shutdown_command = "shutdown /s /t 10 /f /d p:4:1"

  # ── Linux instead? ─────────────────────────────────────────────────────
  # Delete the five WinRM lines above and use:
  #   communicator     = "ssh"
  #   ssh_username     = var.build_username
  #   ssh_password     = var.build_password
  #   ssh_timeout      = "30m"
  #   boot_command     = [...]        # point the installer at your preseed/kickstart
  #   shutdown_command = "echo '<pw>' | sudo -S shutdown -P now"
}

build {
  sources = ["source.qemu.box"]

  # 1. Everything the box needs on disk. Drop files into files/ and they land
  #    here in one step -- ten files or a hundred, same block.
  provisioner "file" {
    source      = "files/"
    destination = "C:/box-files"
  }

  # 2. Configuration, in order. Numbered so the sequence is obvious and a
  #    reviewer can read the box's construction top to bottom.
  provisioner "powershell" {
    scripts = [
      "scripts/00-base.ps1",       # roles, features, updates you actually want
      "scripts/10-registry.ps1",   # registry changes
      "scripts/20-vulnerable.ps1", # install the vulnerable software AT ITS VERSION
      "scripts/30-flag-hook.ps1",  # install the per-run flag planter
      "scripts/99-generalize.ps1", # cleanup + sysprep
    ]
  }
}
