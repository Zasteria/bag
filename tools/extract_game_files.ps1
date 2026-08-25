<#
.SYNOPSIS
    Copy the EU5 game directories this repository needs into reference/game/.

.DESCRIPTION
    reference/game/ deliberately holds only part of EU5 - the parts the mods
    here reason about. When a task needs more, the fix is to copy the missing
    directories in, and doing that by hand means hunting through a hundred
    folders and getting one of them wrong.

    Which directories, and why, is tools/game_files_manifest.txt. This script
    and its Python twin (tools/extract_game_files.py) both read it, so the list
    cannot drift between them.

    A directory that is not where the manifest says gets one search by name
    across the whole install before it is called missing - static_modifiers is
    not under in_game/ at all. On top of that, every .txt in the install that
    mentions 'monthly_towards_' comes along regardless of its folder.

    Existing files are overwritten with the copy from the install - that is what
    a refresh is - and nothing is deleted. git is the undo: run git status
    afterwards to see exactly what the install brought.

.PARAMETER Game
    The Europa Universalis V install folder. Without it, the usual Steam
    locations are tried.

.PARAMETER Out
    Where to write. Defaults to this repository's reference\game.

.EXAMPLE
    .\tools\extract_game_files.ps1

.EXAMPLE
    .\tools\extract_game_files.ps1 -Game "D:\SteamLibrary\steamapps\common\Europa Universalis V"
#>

[CmdletBinding()]
param(
    [string] $Game,
    [string] $Out
)

$ErrorActionPreference = 'Stop'

$toolsDir = if ($PSScriptRoot) { $PSScriptRoot }
            else { Split-Path -Parent $MyInvocation.MyCommand.Path }
$repoDir  = Split-Path -Parent $toolsDir
$manifestFile = Join-Path $toolsDir 'game_files_manifest.txt'

if (-not $Out) { $Out = Join-Path $repoDir 'reference\game' }

# The sweep covers the whole install, not in_game\common alone: the game puts
# some of its own data on other mounts, and static_modifiers - 298 of the
# societal value pushes - is one of those.
$sweepMarker = 'monthly_towards_'

# ---------------------------------------------------------------- find the game

function Find-GameRoot {
    param([string] $Given)

    $roots = if ($Given) { @($Given) } else {
        @(
            "${env:ProgramFiles(x86)}\Steam\steamapps\common\Europa Universalis V",
            "$env:ProgramFiles\Steam\steamapps\common\Europa Universalis V",
            'C:\Steam\steamapps\common\Europa Universalis V',
            'D:\Steam\steamapps\common\Europa Universalis V',
            'D:\SteamLibrary\steamapps\common\Europa Universalis V',
            'E:\SteamLibrary\steamapps\common\Europa Universalis V',
            'F:\SteamLibrary\steamapps\common\Europa Universalis V'
        )
    }

    $tried = @()
    foreach ($root in $roots) {
        # The install root has the game files either at the top or in game\.
        foreach ($inside in @('', 'game')) {
            $candidate = if ($inside) { Join-Path $root $inside } else { $root }
            $tried += $candidate
            if (Test-Path (Join-Path $candidate 'in_game') -PathType Container) {
                return (Resolve-Path $candidate).Path
            }
        }
    }

    Write-Host ''
    Write-Host 'No EU5 game files found. Looked for an in_game folder in:' -ForegroundColor Red
    $tried | ForEach-Object { Write-Host "  $_" }
    Write-Host ''
    Write-Host 'Pass the install folder explicitly:'
    Write-Host '  .\tools\extract_game_files.ps1 -Game "<path to Europa Universalis V>"'
    exit 2
}

function Format-Size {
    param([double] $Bytes)
    foreach ($unit in @('B', 'KB', 'MB', 'GB')) {
        if ($Bytes -lt 1024 -or $unit -eq 'GB') {
            if ($unit -eq 'B') { return ('{0:N0} B' -f $Bytes) }
            return ('{0:N1} {1}' -f $Bytes, $unit)
        }
        $Bytes = $Bytes / 1024
    }
}

# --------------------------------------------------------------------- manifest

if (-not (Test-Path $manifestFile)) {
    Write-Host "No manifest at $manifestFile - is this a full checkout?" -ForegroundColor Red
    exit 2
}

$wanted = [ordered]@{}
foreach ($line in Get-Content -LiteralPath $manifestFile -Encoding UTF8) {
    $trimmed = $line.Trim()
    if (-not $trimmed -or $trimmed.StartsWith('#')) { continue }
    $parts  = $trimmed -split '#', 2
    $relative = $parts[0].Trim().Replace('/', '\')
    $reason   = if ($parts.Count -gt 1) { $parts[1].Trim() } else { '' }
    $wanted[$relative] = $reason
}

# ------------------------------------------------------------------------- copy

$gameRoot = Find-GameRoot -Given $Game
New-Item -ItemType Directory -Force -Path $Out | Out-Null
$outRoot = (Resolve-Path $Out).Path

Write-Host "game:   $gameRoot"
Write-Host "out:    $outRoot"
Write-Host ''

$totalFiles = 0
$totalBytes = 0.0
$missing    = @()
$copiedPaths = New-Object 'System.Collections.Generic.HashSet[string]' ([StringComparer]::OrdinalIgnoreCase)

foreach ($relative in $wanted.Keys) {
    $source  = Join-Path $gameRoot $relative
    $foundAt = $relative

    if (-not (Test-Path $source -PathType Container)) {
        # Not where the manifest says. Look for a directory of that name
        # anywhere in the install before calling it missing.
        $leaf  = Split-Path -Leaf $relative
        $moved = Get-ChildItem -LiteralPath $gameRoot -Recurse -Directory -Filter $leaf -ErrorAction SilentlyContinue |
                 Select-Object -First 1
        if (-not $moved) {
            $missing += ('{0,-46} {1}' -f $relative, $wanted[$relative])
            continue
        }
        $source  = $moved.FullName
        $foundAt = $moved.FullName.Substring($gameRoot.Length).TrimStart('\')
    }

    $files = @(Get-ChildItem -LiteralPath $source -Recurse -File)
    $bytes = 0.0
    foreach ($file in $files) {
        $tail        = $file.FullName.Substring($source.Length).TrimStart('\')
        $destination = Join-Path (Join-Path $outRoot $foundAt) $tail
        $parent      = Split-Path -Parent $destination
        if (-not (Test-Path $parent)) { New-Item -ItemType Directory -Force -Path $parent | Out-Null }
        Copy-Item -LiteralPath $file.FullName -Destination $destination -Force
        [void] $copiedPaths.Add($file.FullName)
        $bytes += $file.Length
    }

    $totalFiles += $files.Count
    $totalBytes += $bytes
    $word = if ($files.Count -eq 1) { 'file ' } else { 'files' }
    $note = if ($foundAt -eq $relative) { '' } else { "   <- found at $foundAt" }
    Write-Host ('  {0,-46} {1,4} {2} {3,9}{4}' -f $relative, $files.Count, $word, (Format-Size $bytes), $note)
}

# ------------------------------------------------------- the sweep, by content

if (Test-Path $gameRoot -PathType Container) {
    Write-Host ''
    Write-Host 'sweeping the install for files that mention the marker...'
    $extra = [ordered]@{}
    foreach ($file in Get-ChildItem -LiteralPath $gameRoot -Recurse -File -Filter '*.txt' -ErrorAction SilentlyContinue) {
        if ($copiedPaths.Contains($file.FullName)) { continue }
        $hit = Select-String -LiteralPath $file.FullName -Pattern $sweepMarker -SimpleMatch -List -ErrorAction SilentlyContinue
        if (-not $hit) { continue }

        $relativeFile = $file.FullName.Substring($gameRoot.Length).TrimStart('\')
        $destination  = Join-Path $outRoot $relativeFile
        $parent       = Split-Path -Parent $destination
        if (-not (Test-Path $parent)) { New-Item -ItemType Directory -Force -Path $parent | Out-Null }
        Copy-Item -LiteralPath $file.FullName -Destination $destination -Force

        $folder = Split-Path -Parent $relativeFile
        if (-not $folder) { $folder = '(top level)' }
        if ($extra.Contains($folder)) { $extra[$folder] += 1 } else { $extra[$folder] = 1 }
        $totalFiles += 1
        $totalBytes += $file.Length
    }

    if ($extra.Count -gt 0) {
        Write-Host ''
        Write-Host "also, by content - files mentioning '$sweepMarker' outside the list above:"
        foreach ($folder in $extra.Keys) {
            $word = if ($extra[$folder] -eq 1) { 'file ' } else { 'files' }
            Write-Host ('  {0,-46} {1,4} {2}' -f $folder, $extra[$folder], $word)
        }
    }
}

# ----------------------------------------------------------------------- report

if ($missing.Count -gt 0) {
    Write-Host ''
    Write-Host 'not in this install, and skipped:'
    $missing | ForEach-Object { Write-Host "  $_" }
    Write-Host ''
    Write-Host 'A folder Paradox renamed is not a problem by itself - the content sweep'
    Write-Host 'above catches the ones that matter. A folder that matters and is missing'
    Write-Host 'from both is worth saying so.'
}

Write-Host ''
Write-Host ('{0} files, {1}.' -f $totalFiles, (Format-Size $totalBytes)) -ForegroundColor Green
Write-Host ''
Write-Host 'Next:'
Write-Host '  git status          # what the install brought'
Write-Host '  git add reference/game'
Write-Host '  git commit -m "reference: game files for the societal value sources"'
Write-Host '  git push'
