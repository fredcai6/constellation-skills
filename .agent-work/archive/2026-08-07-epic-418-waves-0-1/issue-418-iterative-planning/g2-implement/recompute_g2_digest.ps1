$ErrorActionPreference = "Stop"

$g2RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..\..")).Path
$g2InventoryPath = Join-Path $PSScriptRoot "G2_DIGEST_PATHS.txt"
$g2Paths = @(Get-Content -LiteralPath $g2InventoryPath | Where-Object { $_ -ne "" })
$g2Sorted = [string[]]$g2Paths.Clone()
[System.Array]::Sort($g2Sorted, [System.StringComparer]::Ordinal)

if ($g2Paths.Count -ne 11) {
    throw "G2 digest inventory must contain exactly 11 paths; found $($g2Paths.Count)"
}
if (($g2Paths -join "`n") -cne ($g2Sorted -join "`n")) {
    throw "G2 digest inventory is not sorted"
}
if (($g2Paths | Select-Object -Unique).Count -ne $g2Paths.Count) {
    throw "G2 digest inventory contains duplicate paths"
}

$g2Stream = [System.IO.MemoryStream]::new()
try {
    foreach ($g2RelativePath in $g2Paths) {
        $g2Label = [System.Text.Encoding]::UTF8.GetBytes($g2RelativePath + [char]0)
        $g2Stream.Write($g2Label, 0, $g2Label.Length)
        $g2AbsolutePath = Join-Path $g2RepoRoot $g2RelativePath
        if (Test-Path -LiteralPath $g2AbsolutePath -PathType Leaf) {
            $g2Bytes = [System.IO.File]::ReadAllBytes($g2AbsolutePath)
            $g2Stream.Write($g2Bytes, 0, $g2Bytes.Length)
        }
        else {
            $g2Deleted = [System.Text.Encoding]::UTF8.GetBytes("<deleted>")
            $g2Stream.Write($g2Deleted, 0, $g2Deleted.Length)
        }
        $g2Stream.WriteByte(0)
    }
    $g2Stream.Position = 0
    $g2Sha256 = [System.Security.Cryptography.SHA256]::Create()
    try {
        $g2Hash = $g2Sha256.ComputeHash($g2Stream)
    }
    finally {
        $g2Sha256.Dispose()
    }
}
finally {
    $g2Stream.Dispose()
}

$g2Hex = [System.BitConverter]::ToString($g2Hash).Replace("-", "").ToLowerInvariant()
Write-Output "sha256:$g2Hex"
