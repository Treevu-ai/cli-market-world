$ErrorActionPreference = "Stop"
$Patch = if ($PSScriptRoot) { $PSScriptRoot } else { Split-Path -Parent $MyInvocation.MyCommand.Path }
python (Join-Path $Patch "apply.py") --target (Get-Location) --patch $Patch
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
