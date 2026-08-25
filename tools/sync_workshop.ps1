<#
.SYNOPSIS
    Bring the workshop copies of the tracked mods into reference/ and push them.

.DESCRIPTION
    The loop this replaces was: notice a mod updated, unsubscribe and resubscribe
    so Steam actually fetches it, find the folder under steamapps, copy it into
    the repository, work out what the folder should be called this time, commit,
    push. Six steps, each of which has gone wrong at least once.

    This is those six steps. It reads tools/workshop_mods.txt for which items to
    take - the same file the Python twin and the GitHub check read, so the list
    cannot drift - copies each one in whole, rebuilds everything generated from
    them (when Python is on this box), commits, and pushes.

    Nothing has to be told what the folders are called. A folder already carrying
    the workshop id keeps its name; anything else is renamed to
    <workshop id>_<the id inside the mod's own metadata>, and a second copy of the
    same mod under an older name is removed - two copies of one mod is the state
    that makes tools/refs.py refuse to answer.

    Anonymous downloading does not work for this game: steamcmd answers
    'Download item failed (Failure)' without an account that owns EU5. That was
    measured. So this runs where the files already are, which is this box.

.PARAMETER From
    steamapps\workshop\content, or that folder's 3450310 inside it. Without it,
    Steam's own library list is read and every library is tried.

.PARAMETER SteamCmd
    Path to steamcmd.exe. Given it, the tracked items are downloaded fresh before
    copying, which is what removes the unsubscribe-resubscribe dance: steamcmd
    fetches the current version on demand whatever the Steam client believes.
    Needs -Login, and the first login on a machine has to be done by hand once so
    Steam Guard is satisfied.

.PARAMETER Only
    Workshop ids or keys from tools/workshop_mods.txt. Default is all of them.

.PARAMETER Branch
    Branch to push to. Default is whatever is checked out.

.PARAMETER Playset
    Also refresh reference\playset - a text-only copy of every other mod you are
    subscribed to, for reading and measuring. No textures, no sound, English and
    Russian localization only. Needs Python on this box.

.PARAMETER CheckPython
    Report which Python this script would use, and where it looked, then stop.
    Nothing is copied, committed or pushed.

.PARAMETER NoCommit
    Copy and rebuild, but leave the result in the working tree uncommitted.

.PARAMETER NoPush
    Commit but do not push.

.PARAMETER DryRun
    Say what would be copied and stop.

.EXAMPLE
    .\tools\sync_workshop.ps1

.EXAMPLE
    .\tools\sync_workshop.ps1 -Only national_destinies auto_build

.EXAMPLE
    .\tools\sync_workshop.ps1 -SteamCmd C:\steamcmd\steamcmd.exe -Login myaccount

.EXAMPLE
    .\tools\sync_workshop.ps1 -Playset
#>

[CmdletBinding()]
param(
    [string]   $From,
    [string]   $SteamCmd,
    [string]   $Login,
    [string[]] $Only,
    [string]   $Branch,
    [switch]   $Playset,
    [switch]   $CheckPython,
    [switch]   $NoCommit,
    [switch]   $NoPush,
    [switch]   $DryRun
)

$ErrorActionPreference = 'Stop'
# git says what it means through its exit code - `git diff --cached --quiet`
# answers 1 for "there are changes", and a shell that treats that as a thrown
# error stops the script exactly where it has something to do.
if (Get-Variable -Name PSNativeCommandUseErrorActionPreference -ErrorAction SilentlyContinue) {
    $PSNativeCommandUseErrorActionPreference = $false
}

# Europa Universalis V. Its workshop items live under
# steamapps\workshop\content\3450310\<item id>\.
$AppId = '3450310'

$toolsDir = if ($PSScriptRoot) { $PSScriptRoot }
            else { Split-Path -Parent $MyInvocation.MyCommand.Path }
$repoDir  = Split-Path -Parent $toolsDir

. (Join-Path $toolsDir 'find_python.ps1')

if ($CheckPython) {
    Write-Host 'Looking for Python the way this script does:'
    $found = Find-Python -Explain
    if ($found) {
        Write-Host ''
        Write-Host "This is what a sync would use: $found" -ForegroundColor Green
        exit 0
    }
    Write-Host ''
    Write-Host 'A sync would copy and push, and skip the rebuild.' -ForegroundColor Red
    exit 1
}

$modsDir  = Join-Path $repoDir 'reference\mods'
$manifest = Join-Path $toolsDir 'workshop_mods.txt'

# ------------------------------------------------------------------ the tracked

if (-not (Test-Path $manifest)) {
    Write-Host "No manifest at $manifest - is this a full checkout?" -ForegroundColor Red
    exit 2
}

$tracked = @()
foreach ($line in Get-Content -LiteralPath $manifest -Encoding UTF8) {
    $trimmed = $line.Trim()
    if (-not $trimmed -or $trimmed.StartsWith('#')) { continue }
    $body = ($trimmed -split '#', 2)[0].Trim()
    $parts = $body -split '\s+'
    if ($parts.Count -lt 2) { continue }
    $tracked += [pscustomobject]@{ Id = $parts[0]; Key = $parts[1] }
}

if ($Only) {
    $wanted  = $Only | ForEach-Object { $_.ToLower() }
    $tracked = $tracked | Where-Object { $wanted -contains $_.Id -or $wanted -contains $_.Key.ToLower() }
    if (-not $tracked) {
        Write-Host "Nothing tracked matches: $($Only -join ', ')" -ForegroundColor Red
        exit 2
    }
}

# --------------------------------------------------------------- where Steam is

function Get-SteamLibraries {
    $roots = @()
    foreach ($key in @('HKCU:\Software\Valve\Steam', 'HKLM:\SOFTWARE\WOW6432Node\Valve\Steam')) {
        try {
            $property = Get-ItemProperty -Path $key -ErrorAction Stop
            foreach ($name in @('SteamPath', 'InstallPath')) {
                if ($property.$name) { $roots += ($property.$name -replace '/', '\') }
            }
        } catch { }
    }
    $roots += @(
        "${env:ProgramFiles(x86)}\Steam",
        "$env:ProgramFiles\Steam"
    )

    # Every library Steam knows about, not just the one it is installed in - the
    # game is as likely to be on a second drive as on C:.
    $libraries = @()
    foreach ($root in ($roots | Where-Object { $_ } | Select-Object -Unique)) {
        $libraries += $root
        $vdf = Join-Path $root 'steamapps\libraryfolders.vdf'
        if (Test-Path $vdf) {
            foreach ($match in [regex]::Matches((Get-Content -LiteralPath $vdf -Raw), '"path"\s+"([^"]+)"')) {
                $libraries += ($match.Groups[1].Value -replace '\\\\', '\')
            }
        }
    }
    return $libraries | Select-Object -Unique
}

function Find-Content {
    param([string] $Given)

    if ($Given) {
        foreach ($candidate in @((Join-Path $Given $AppId), $Given)) {
            if (Test-Path $candidate -PathType Container) { return (Resolve-Path $candidate).Path }
        }
        Write-Host "No such folder: $Given" -ForegroundColor Red
        exit 2
    }

    $tried = @()
    foreach ($library in Get-SteamLibraries) {
        $candidate = Join-Path $library "steamapps\workshop\content\$AppId"
        $tried += $candidate
        if (Test-Path $candidate -PathType Container) { return (Resolve-Path $candidate).Path }
    }

    Write-Host ''
    Write-Host "No workshop content for app $AppId found. Looked in:" -ForegroundColor Red
    $tried | ForEach-Object { Write-Host "  $_" }
    Write-Host ''
    Write-Host 'Pass it explicitly:'
    Write-Host '  .\tools\sync_workshop.ps1 -From "D:\SteamLibrary\steamapps\workshop\content"'
    exit 2
}

# ---------------------------------------------------------------- steamcmd first

if ($SteamCmd) {
    if (-not (Test-Path $SteamCmd)) {
        Write-Host "No steamcmd at $SteamCmd" -ForegroundColor Red
        exit 2
    }
    $account = if ($Login) { $Login } else { 'anonymous' }
    if (-not $Login) {
        Write-Host 'steamcmd without -Login can only log in anonymously, and this game refuses that.' -ForegroundColor Yellow
    }
    $arguments = @('+login', $account)
    foreach ($item in $tracked) { $arguments += @('+workshop_download_item', $AppId, $item.Id) }
    $arguments += '+quit'
    Write-Host "steamcmd: fetching $($tracked.Count) item(s) as $account"
    & $SteamCmd @arguments
    if (-not $From) {
        $From = Join-Path (Split-Path -Parent (Resolve-Path $SteamCmd)) "steamapps\workshop\content"
    }
}

$content = Find-Content -Given $From

# ------------------------------------------------------------ what is here now

function Get-ModId {
    param([string] $Folder)
    foreach ($name in @('.metadata\metadata.json', 'metadata\metadata.json')) {
        $file = Join-Path $Folder $name
        if (Test-Path $file) {
            try {
                $text = [System.IO.File]::ReadAllText($file)
                return (ConvertFrom-Json $text.TrimStart([char]0xFEFF)).id
            } catch { return $null }
        }
    }
    return $null
}

function Get-Slug {
    param([string] $Text)
    $slug = ($Text.ToLower() -replace '[^a-z0-9]', '_')
    while ($slug -match '__') { $slug = $slug -replace '__', '_' }
    return $slug.Trim('_')
}

$existing = @()
if (Test-Path $modsDir) {
    foreach ($folder in Get-ChildItem -LiteralPath $modsDir -Directory) {
        $existing += [pscustomobject]@{
            Path = $folder.FullName
            Name = $folder.Name
            Id   = Get-ModId -Folder $folder.FullName
        }
    }
}

Write-Host "from:   $content"
Write-Host "into:   $modsDir"
Write-Host ''

# ------------------------------------------------------------------------- copy

$copied = @()
foreach ($item in $tracked) {
    $source = Join-Path $content $item.Id
    if (-not (Test-Path $source -PathType Container)) {
        Write-Host ('  {0,-22} not in the workshop folder - Steam has not downloaded it' -f $item.Key)
        continue
    }

    $sourceId = Get-ModId -Folder $source
    $mine = $existing | Where-Object { $_.Name -like "*$($item.Id)*" -or ($sourceId -and $_.Id -eq $sourceId) }
    $keep = $mine | Where-Object { $_.Name -like "*$($item.Id)*" } | Select-Object -First 1

    $folderName = if ($keep) { $keep.Name }
                  else { '{0}_{1}' -f $item.Id, (Get-Slug ($(if ($sourceId) { $sourceId } else { $item.Key }))) }
    $target = Join-Path $modsDir $folderName

    if ($DryRun) {
        Write-Host ('  {0,-22} would replace {1}' -f $item.Key, $folderName)
        continue
    }

    # Wholesale, not merged: an update that deletes a file has to delete it here
    # too, or a generator goes on compiling from a file the mod no longer ships.
    if (Test-Path $target) { Remove-Item -LiteralPath $target -Recurse -Force }
    New-Item -ItemType Directory -Force -Path $target | Out-Null
    # Entry by entry, with -Force, because the mod's own .metadata folder is the
    # one thing here that nothing else can identify the mod by.
    foreach ($entry in Get-ChildItem -LiteralPath $source -Force) {
        Copy-Item -LiteralPath $entry.FullName -Destination $target -Recurse -Force
    }

    $files = @(Get-ChildItem -LiteralPath $target -Recurse -File -Force)
    $bytes = ($files | Measure-Object -Property Length -Sum).Sum
    $note  = ''
    foreach ($stale in ($mine | Where-Object { $_.Name -ne $folderName })) {
        Remove-Item -LiteralPath $stale.Path -Recurse -Force -ErrorAction SilentlyContinue
        $note = "   (replaced $($stale.Name))"
    }
    $copied += $item.Key
    Write-Host ('  {0,-22} {1,-40} {2,4} files {3,8:N1} MB{4}' -f $item.Key, $folderName, $files.Count, ($bytes / 1MB), $note)
}

if ($DryRun) {
    Write-Host ''
    Write-Host '-DryRun: nothing written.'
    exit 0
}
if (-not $copied) {
    Write-Host ''
    Write-Host 'Nothing copied.' -ForegroundColor Yellow
    exit 1
}

# ----------------------------------------------------- rebuild what is generated

# Python's own output is Russian in places, and PowerShell reads a native
# command through a pipe rather than a console - which puts Python on the
# machine's ANSI code page, where a Cyrillic line raises UnicodeEncodeError and
# takes the rest of the run with it. UTF-8 both ways instead.
$env:PYTHONUTF8 = '1'
$env:PYTHONIOENCODING = 'utf-8'
try { [Console]::OutputEncoding = [System.Text.Encoding]::UTF8 } catch { }

$python = Find-Python

Push-Location $repoDir
try {
    if ($python) {
        Write-Host ''
        & $python (Join-Path $toolsDir 'refresh.py')
        Write-Host ''
        & $python (Join-Path $toolsDir 'workshop.py') 'record'
        if ($Playset) {
            Write-Host ''
            & $python (Join-Path $toolsDir 'workshop.py') 'playset' '--from' $content
        }
    } else {
        Write-Host ''
        Write-Host 'NO PYTHON FOUND ON THIS BOX.' -ForegroundColor Red
        Write-Host 'The workshop copies below are still committed and pushed - that part is done -' -ForegroundColor Yellow
        Write-Host 'but nothing generated from them was rebuilt, so a translation whose English has' -ForegroundColor Yellow
        Write-Host 'moved will not have said so yet. Two ways on:' -ForegroundColor Yellow
        Write-Host ''
        Write-Host '  - ask the next session to run tools/refresh.py - it reports what the update moved;' -ForegroundColor Yellow
        Write-Host '  - or install Python once and this step runs itself from now on:' -ForegroundColor Yellow
        Write-Host '      winget install -e --id Python.Python.3.12' -ForegroundColor Yellow
        Write-Host ''
        Write-Host 'The update check is unaffected: it works out from git that these copies are' -ForegroundColor Yellow
        Write-Host 'current, whether or not `workshop.py record` ever ran here.' -ForegroundColor Yellow
        if ($Playset) {
            Write-Host '-Playset needs Python too, so the playset copies were not refreshed either.' -ForegroundColor Yellow
        }
    }

    # ------------------------------------------------------------------ commit

    if ($NoCommit) {
        Write-Host ''
        Write-Host 'not committed (-NoCommit). `git status` for what the update brought.'
        exit 0
    }

    git add -- reference mods
    git diff --cached --quiet
    if ($LASTEXITCODE -eq 0) {
        Write-Host ''
        Write-Host 'Nothing changed - the copies here were already the current ones.'
        exit 0
    }

    $message = 'reference: {0} from the workshop' -f ($copied -join ', ')
    git commit -m $message
    Write-Host ''
    Write-Host "committed: $message" -ForegroundColor Green

    if ($NoPush) {
        Write-Host 'not pushed (-NoPush).'
        exit 0
    }

    $target = if ($Branch) { $Branch } else { (git rev-parse --abbrev-ref HEAD).Trim() }
    foreach ($wait in @(2, 4, 8, 16, 0)) {
        git push -u origin $target
        if ($LASTEXITCODE -eq 0) {
            Write-Host "pushed to $target" -ForegroundColor Green
            exit 0
        }
        if ($wait -gt 0) {
            Write-Host "push failed, retrying in ${wait}s" -ForegroundColor Yellow
            Start-Sleep -Seconds $wait
        }
    }
    Write-Host 'push failed.' -ForegroundColor Red
    exit 1
} finally {
    Pop-Location
}
