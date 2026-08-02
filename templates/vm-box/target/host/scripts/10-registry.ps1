# Registry changes.
#
# Ten of them or a hundred, this is where they go -- one line each, in a file
# a reviewer can read. Prefer New-ItemProperty/Set-ItemProperty over `reg add`
# so a failure stops the build instead of scrolling past.
$ErrorActionPreference = "Stop"

# Example: weaken a setting the challenge depends on. Every line here should be
# something the box NEEDS -- a reviewer will ask why each one is present.
New-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\Lsa" `
  -Name "LmCompatibilityLevel" -Value 1 -PropertyType DWord -Force | Out-Null

# Example: an autologon credential left behind, the classic "found in the
# registry" foothold.
$winlogon = "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon"
Set-ItemProperty -Path $winlogon -Name "DefaultUserName" -Value "svc_backup"
Set-ItemProperty -Path $winlogon -Name "DefaultPassword" -Value "Backup!2019"

Write-Host "registry configured"
