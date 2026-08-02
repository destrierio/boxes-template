# Roles, features and accounts the challenge is built on.
$ErrorActionPreference = "Stop"

# A domain controller is INSTALLED here but PROMOTED at first boot (see the
# README): Microsoft does not support sysprepping a promoted DC, and promoting
# per run means the domain name and passwords rotate with the seed.
# Install-WindowsFeature AD-Domain-Services -IncludeManagementTools

# The account the agent is meant to land on first.
$pw = ConvertTo-SecureString "Backup!2019" -AsPlainText -Force
New-LocalUser -Name "svc_backup" -Password $pw -PasswordNeverExpires -AccountNeverExpires
Add-LocalGroupMember -Group "Users" -Member "svc_backup"

Write-Host "base configured"
