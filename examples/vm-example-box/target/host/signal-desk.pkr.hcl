packer {
  required_plugins {
    qemu = {
      version = ">= 1.1.0"
      source  = "github.com/hashicorp/qemu"
    }
  }
}

variable "iso_url" {
  type    = string
  default = "https://cloud-images.ubuntu.com/noble/current/noble-server-cloudimg-amd64.img"
}

variable "iso_checksum" {
  type    = string
  default = "file:https://cloud-images.ubuntu.com/noble/current/SHA256SUMS"
}

variable "ssh_username" {
  type    = string
  default = "destrier"
}

variable "ssh_password" {
  type    = string
  default = "destrier"
}

source "qemu" "host" {
  accelerator      = "none"
  cd_files         = ["cloud-init/user-data", "cloud-init/meta-data"]
  cd_label         = "cidata"
  communicator     = "ssh"
  cpus             = 1
  disk_image       = true
  format           = "qcow2"
  headless         = true
  iso_checksum     = var.iso_checksum
  iso_url          = var.iso_url
  memory           = 1024
  output_directory = "output-signal-desk"
  shutdown_command = "echo '${var.ssh_password}' | sudo -S shutdown -P now"
  ssh_password     = var.ssh_password
  ssh_timeout      = "20m"
  ssh_username     = var.ssh_username
  vm_name          = "signal-desk"
}

build {
  sources = ["source.qemu.host"]

  provisioner "shell" {
    execute_command = "sudo -E sh -c '{{ .Vars }} {{ .Path }}'"
    script          = "provision.sh"
  }
}
