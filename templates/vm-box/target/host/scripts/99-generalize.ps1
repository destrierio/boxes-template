# Cleanup and generalize.
#
# Remove the build credentials -- they are Packer's way in, not a solve path --
# then sysprep so every run boots a fresh identity.
$ErrorActionPreference = "Stop"

Remove-LocalUser -Name "packer" -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force "C:\box-files" -ErrorAction SilentlyContinue

# GCESysprep on GCP images; plain sysprep for a qcow2 booted under QEMU.
& "$env:WINDIR\System32\Sysprep\Sysprep.exe" /generalize /oobe /shutdown /quiet
