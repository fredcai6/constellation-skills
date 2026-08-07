$ErrorActionPreference = "Stop"

$g1RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..\..")).Path
$g1InventoryPath = Join-Path $PSScriptRoot "G1_DIGEST_PATHS.txt"
$g1Paths = @(Get-Content -LiteralPath $g1InventoryPath | Where-Object { $_ -ne "" })
$g1Sorted = [string[]]$g1Paths.Clone()
[System.Array]::Sort($g1Sorted, [System.StringComparer]::Ordinal)

if ($g1Paths.Count -ne 20) {
    throw "G1 digest inventory must contain exactly 20 paths; found $($g1Paths.Count)"
}
if (($g1Paths -join "`n") -cne ($g1Sorted -join "`n")) {
    throw "G1 digest inventory is not sorted"
}
if (($g1Paths | Select-Object -Unique).Count -ne $g1Paths.Count) {
    throw "G1 digest inventory contains duplicate paths"
}

$g1Stream = [System.IO.MemoryStream]::new()
try {
    foreach ($g1RelativePath in $g1Paths) {
        $g1Label = [System.Text.Encoding]::UTF8.GetBytes($g1RelativePath + [char]0)
        $g1Stream.Write($g1Label, 0, $g1Label.Length)
        $g1AbsolutePath = Join-Path $g1RepoRoot $g1RelativePath
        if (Test-Path -LiteralPath $g1AbsolutePath -PathType Leaf) {
            $g1Bytes = [System.IO.File]::ReadAllBytes($g1AbsolutePath)
            $g1Stream.Write($g1Bytes, 0, $g1Bytes.Length)
        }
        else {
            $g1Deleted = [System.Text.Encoding]::UTF8.GetBytes("<deleted>")
            $g1Stream.Write($g1Deleted, 0, $g1Deleted.Length)
        }
        $g1Stream.WriteByte(0)
    }
    $g1Stream.Position = 0
    $g1Sha256 = [System.Security.Cryptography.SHA256]::Create()
    try {
        $g1Hash = $g1Sha256.ComputeHash($g1Stream)
    }
    finally {
        $g1Sha256.Dispose()
    }
}
finally {
    $g1Stream.Dispose()
}

$g1Hex = [System.BitConverter]::ToString($g1Hash).Replace("-", "").ToLowerInvariant()
Write-Output "sha256:$g1Hex"
