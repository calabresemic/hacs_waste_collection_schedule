<#
.SYNOPSIS
    Step 2: delete the two source-catalogue files that the simplified config
    flow no longer reads.

.DESCRIPTION
    Run from anywhere inside the repository:

        .\simplify_step2_delete.ps1

    or, if PowerShell blocks it:

        powershell -ExecutionPolicy Bypass -File .\simplify_step2_delete.ps1

    Everything else in this round is a file edit and has already been written
    to your working tree. Nothing is committed - review with `git status`.
#>

$ErrorActionPreference = 'Stop'

$root = & git rev-parse --show-toplevel 2>$null
if ($LASTEXITCODE -ne 0 -or -not $root) {
    throw 'Not inside a git repository - cd into the repo first.'
}
Set-Location $root

$CC = 'custom_components/waste_collection_schedule'

Write-Host '==> Removing the source catalogue (now module constants in config_flow.py)'
& git rm -q --ignore-unmatch -- "$CC/sources.json" "$CC/source_metadata.json"
if ($LASTEXITCODE -ne 0) { throw "git rm failed with exit code $LASTEXITCODE" }

Remove-Item -Force -ErrorAction SilentlyContinue 'simplify_step1_delete.ps1'

Write-Host ''
Write-Host "==> Done. $((& git ls-files).Count) tracked files remain."
Write-Host "    Review with 'git status'."
