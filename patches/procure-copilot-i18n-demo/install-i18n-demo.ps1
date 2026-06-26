# Procure i18n + demo CTA patch
$ErrorActionPreference = "Stop"
$RepoRoot = $PSScriptRoot
if (-not (Test-Path "$RepoRoot\apply.py")) {
    $RepoRoot = Join-Path $env:TEMP "procure-i18n-demo-patch"
    New-Item -ItemType Directory -Force -Path $RepoRoot | Out-Null
    $base = "https://raw.githubusercontent.com/Treevu-ai/cli-market-world/main/patches/procure-copilot-i18n-demo"
    @(
        "apply.py",
        "README.md",
        "lib/procureCta.ts",
        "lib/i18n.ts",
        "lib/LanguageContext.tsx",
        "lib/procureLocale.ts",
        "components/LangToggle.tsx"
    ) | ForEach-Object {
        $dest = Join-Path $RepoRoot $_
        $dir = Split-Path $dest -Parent
        if ($dir) { New-Item -ItemType Directory -Force -Path $dir | Out-Null }
        Invoke-WebRequest "$base/$_" -OutFile $dest
    }
}
$Target = Get-Location
python (Join-Path $RepoRoot "apply.py") --target $Target --patch $RepoRoot
