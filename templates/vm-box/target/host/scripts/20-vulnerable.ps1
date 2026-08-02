# The vulnerability itself.
#
# For a CVE box this is the whole point: install the software AT THE AFFECTED
# VERSION and leave it reachable. Pin the version explicitly -- "latest" will
# silently patch your box out of existence on the next rebuild, and the box
# will look solved-proof while actually being unsolvable.
$ErrorActionPreference = "Stop"

# Pin it. Name the CVE. A reviewer (and future you) needs to know what this is.
$CVE     = "CVE-XXXX-YYYYY"
$Version = "1.2.3"                     # the AFFECTED version, never "latest"
$Source  = "C:\box-files\vulnerable-app-$Version.msi"

Write-Host "installing $Source for $CVE"
Start-Process msiexec.exe -ArgumentList "/i `"$Source`" /qn" -Wait -NoNewWindow

# Make it reachable. The port here must match what box.yaml declares, or the
# hop in front of this host will not be listening on it and the service is
# invisible to the agent.
New-NetFirewallRule -DisplayName "box-service" -Direction Inbound `
  -Protocol TCP -LocalPort 8080 -Action Allow | Out-Null

Write-Host "$CVE surface installed and reachable on 8080"
