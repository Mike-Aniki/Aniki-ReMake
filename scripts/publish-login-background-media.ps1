param(
    [Parameter(Mandatory = $true)]
    [string]$ThemeFolder,

    [string]$Repo = "Mike-Aniki/Aniki-ReMake",
    [string]$Tag = "login-backgrounds-v1"
)

$ErrorActionPreference = "Stop"

if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
    throw "GitHub CLI (gh) is required. Install it, run 'gh auth login', then run this script again."
}

$repoRoot = Split-Path -Parent $PSScriptRoot
$catalogPath = Join-Path $repoRoot "media-catalog.json"
$videoFolder = Join-Path $ThemeFolder "Startup Video"

if (-not (Test-Path $catalogPath)) {
    throw "media-catalog.json was not found at $catalogPath"
}
if (-not (Test-Path $videoFolder)) {
    throw "Startup Video folder was not found at $videoFolder"
}

$catalog = Get-Content $catalogPath -Raw -Encoding UTF8 | ConvertFrom-Json
if ($catalog.releaseTag -ne $Tag) {
    throw "Catalog releaseTag '$($catalog.releaseTag)' does not match requested tag '$Tag'."
}

$assets = @()
foreach ($item in $catalog.items) {
    $path = Join-Path $videoFolder $item.fileName
    if (-not (Test-Path $path)) {
        throw "Missing video: $path"
    }

    $actualSize = (Get-Item $path).Length
    if ($actualSize -ne [int64]$item.size) {
        throw "Size mismatch for '$($item.fileName)'. Expected $($item.size), got $actualSize."
    }

    $actualHash = (Get-FileHash -Algorithm SHA256 -Path $path).Hash.ToLowerInvariant()
    if ($actualHash -ne $item.sha256.ToLowerInvariant()) {
        throw "SHA-256 mismatch for '$($item.fileName)'. The catalog and local file are not the same version."
    }

    $assets += $path
}

$releaseExists = $true
try {
    gh release view $Tag --repo $Repo *> $null
}
catch {
    $releaseExists = $false
}

if (-not $releaseExists) {
    Write-Host "Creating release $Tag..."
    gh release create $Tag --repo $Repo --title "Optional Login Backgrounds" --notes "Optional Aniki ReMake Login Screen background videos downloaded on demand by Aniki Helper." --latest=false
}

Write-Host "Uploading $($assets.Count) login background videos..."
foreach ($asset in $assets) {
    Write-Host "  -> $(Split-Path $asset -Leaf)"
    gh release upload $Tag $asset --repo $Repo --clobber
}

Write-Host "Done. Release assets uploaded successfully."
