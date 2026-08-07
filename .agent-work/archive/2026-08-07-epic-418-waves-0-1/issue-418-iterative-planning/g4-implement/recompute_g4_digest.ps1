$ErrorActionPreference = "Stop"

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..\..")).Path
$inventoryPath = Join-Path $PSScriptRoot "G4_DIGEST_PATHS.txt"
$paths = @(Get-Content -LiteralPath $inventoryPath | Where-Object { $_ -ne "" })
$sorted = [string[]]$paths.Clone()
[System.Array]::Sort($sorted, [System.StringComparer]::Ordinal)

if ($paths.Count -ne 39) {
    throw "G4 whole-change digest inventory must contain exactly 39 paths; found $($paths.Count)"
}
if (($paths -join "`n") -cne ($sorted -join "`n")) {
    throw "G4 digest inventory is not ordinal-sorted"
}
if (($paths | Select-Object -Unique).Count -ne $paths.Count) {
    throw "G4 digest inventory contains duplicate paths"
}

$stream = [System.IO.MemoryStream]::new()
try {
    foreach ($relativePath in $paths) {
        $label = [System.Text.Encoding]::UTF8.GetBytes($relativePath + [char]0)
        $stream.Write($label, 0, $label.Length)
        $absolutePath = Join-Path $repoRoot $relativePath
        if (Test-Path -LiteralPath $absolutePath -PathType Leaf) {
            $bytes = [System.IO.File]::ReadAllBytes($absolutePath)
            $stream.Write($bytes, 0, $bytes.Length)
        }
        else {
            $deleted = [System.Text.Encoding]::UTF8.GetBytes("<deleted>")
            $stream.Write($deleted, 0, $deleted.Length)
        }
        $stream.WriteByte(0)
    }
    $stream.Position = 0
    $sha256 = [System.Security.Cryptography.SHA256]::Create()
    try {
        $hash = $sha256.ComputeHash($stream)
    }
    finally {
        $sha256.Dispose()
    }
}
finally {
    $stream.Dispose()
}

$hex = [System.BitConverter]::ToString($hash).Replace("-", "").ToLowerInvariant()
Write-Output "sha256:$hex"
