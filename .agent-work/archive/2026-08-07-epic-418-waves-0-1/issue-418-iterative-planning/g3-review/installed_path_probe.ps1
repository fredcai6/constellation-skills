$ErrorActionPreference = "Stop"

$g3Repo = (Resolve-Path (Join-Path $PSScriptRoot "..\..\..")).Path
$g3Layout = Join-Path $PSScriptRoot "installed-layout"
if (Test-Path -LiteralPath $g3Layout) {
    throw "refusing existing probe layout: $g3Layout"
}

New-Item -ItemType Directory -Path $g3Layout | Out-Null
$g3Installs = @{
    "explorer" = "constellation-explorer"
    "commander" = "constellation-commander"
    "admiral" = "constellation-admiral"
    "replan" = "constellation-replan"
    "to-initial-issues" = "constellation-to-initial-issues"
}
foreach ($g3Pair in $g3Installs.GetEnumerator()) {
    Copy-Item -Recurse -LiteralPath (Join-Path $g3Repo ("skills\" + $g3Pair.Key)) -Destination (Join-Path $g3Layout $g3Pair.Value)
}

$g3ExplorerRoot = Join-Path $g3Layout "constellation-explorer"
$g3CommanderRoot = Join-Path $g3Layout "constellation-commander"
$g3AdmiralRoot = Join-Path $g3Layout "constellation-admiral"

$g3Explorer = Get-Content -Raw (Join-Path $g3ExplorerRoot "templates\EXPLORER_SPINE.template.json") | ConvertFrom-Json
$g3Commander = Get-Content -Raw (Join-Path $g3CommanderRoot "templates\COMMANDER_SPINE.template.json") | ConvertFrom-Json
$g3Admiral = Get-Content -Raw (Join-Path $g3AdmiralRoot "templates\ADMIRAL_SPINE.template.json") | ConvertFrom-Json

$g3Checks = @(
    @{ role = "explorer"; root = $g3ExplorerRoot; relative = $g3Explorer.tasks.confirm.directives.shaped_brief.template },
    @{ role = "commander"; root = $g3CommanderRoot; relative = $g3Commander.tasks.execute.directives.replan_input.template },
    @{ role = "admiral-input"; root = $g3AdmiralRoot; relative = $g3Admiral.tasks.execute.directives.wave_transition.input_template },
    @{ role = "admiral-result"; root = $g3AdmiralRoot; relative = $g3Admiral.tasks.execute.directives.wave_transition.result_template }
)

$g3Failures = 0
foreach ($g3Check in $g3Checks) {
    $g3Resolved = [System.IO.Path]::GetFullPath((Join-Path $g3Check.root $g3Check.relative))
    $g3Exists = Test-Path -LiteralPath $g3Resolved -PathType Leaf
    Write-Output ("{0}: {1} -> {2} (exists={3})" -f $g3Check.role, $g3Check.relative, $g3Resolved, $g3Exists)
    if (-not $g3Exists) { $g3Failures++ }
}

Write-Output "unresolved=$g3Failures inspected=$($g3Checks.Count)"
if ($g3Failures -ne 0) { exit 1 }
