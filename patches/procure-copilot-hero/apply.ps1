# Apply Procure hero patch from cli-market-world
$ErrorActionPreference = "Stop"
$Patch = if ($PSScriptRoot) { $PSScriptRoot } else { Split-Path -Parent $MyInvocation.MyCommand.Path }
$Target = Get-Location
python (Join-Path $Patch "apply.py") --target $Target --patch $Patch
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
