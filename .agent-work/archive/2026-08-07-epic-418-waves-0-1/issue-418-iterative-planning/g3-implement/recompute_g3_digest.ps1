$ErrorActionPreference = "Stop"

$g3RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..\..")).Path
$g3InventoryPath = Join-Path $PSScriptRoot "G3_DIGEST_PATHS.txt"
$g3Paths = @(Get-Content -LiteralPath $g3InventoryPath | Where-Object { $_ -ne "" })
$g3Sorted = [string[]]$g3Paths.Clone()
[System.Array]::Sort($g3Sorted, [System.StringComparer]::Ordinal)

if ($g3Paths.Count -ne 9) {
    throw "G3 digest inventory must contain exactly 9 paths; found $($g3Paths.Count)"
}
if (($g3Paths -join "`n") -cne ($g3Sorted -join "`n")) {
    throw "G3 digest inventory is not sorted"
}
if (($g3Paths | Select-Object -Unique).Count -ne $g3Paths.Count) {
    throw "G3 digest inventory contains duplicate paths"
}

$g3Stream = [System.IO.MemoryStream]::new()
try {
    foreach ($g3RelativePath in $g3Paths) {
        $g3Label = [System.Text.Encoding]::UTF8.GetBytes($g3RelativePath + [char]0)
        $g3Stream.Write($g3Label, 0, $g3Label.Length)
        $g3AbsolutePath = Join-Path $g3RepoRoot $g3RelativePath
        if (Test-Path -LiteralPath $g3AbsolutePath -PathType Leaf) {
            $g3Bytes = [System.IO.File]::ReadAllBytes($g3AbsolutePath)
            $g3Stream.Write($g3Bytes, 0, $g3Bytes.Length)
        }
        else {
            $g3Deleted = [System.Text.Encoding]::UTF8.GetBytes("<deleted>")
            $g3Stream.Write($g3Deleted, 0, $g3Deleted.Length)
        }
        $g3Stream.WriteByte(0)
    }
    $g3Stream.Position = 0
    $g3Sha256 = [System.Security.Cryptography.SHA256]::Create()
    try {
        $g3Hash = $g3Sha256.ComputeHash($g3Stream)
    }
    finally {
        $g3Sha256.Dispose()
    }
}
finally {
    $g3Stream.Dispose()
}

$g3Hex = [System.BitConverter]::ToString($g3Hash).Replace("-", "").ToLowerInvariant()
Write-Output "sha256:$g3Hex"
