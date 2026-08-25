<#
.SYNOPSIS
    Where Python is on this machine. Dot-source it; it defines Find-Python.

.DESCRIPTION
    Split out of tools\sync_workshop.ps1 so tools\mods.ps1 finds Python exactly
    the same way. The rules are there because getting them wrong cost a whole
    sync: an install made without ticking "Add python.exe to PATH" answers to
    none of the names Get-Command knows, and Windows ships a python.exe stub
    that opens the Microsoft Store and runs nothing at all.

    . (Join-Path $PSScriptRoot 'find_python.ps1')
    $python = Find-Python
#>

# Python is looked for where Windows actually keeps it, not only on PATH.
# An install made without ticking "Add python.exe to PATH" is invisible to
# Get-Command and perfectly usable otherwise - which is how the first sync came
# to skip the rebuild on a machine that had Python installed all along. So the
# registry is asked first: every python.org and Store install records itself
# under Software\Python\<company>\<tag>\InstallPath whether or not PATH knows.
#
# Windows also ships a python.exe stub that opens the Microsoft Store and runs
# nothing, so a candidate counts only once it has answered --version.
function Get-PythonCandidates {
    $candidates = @()

    foreach ($hive in @('HKCU:\Software\Python', 'HKLM:\SOFTWARE\Python',
                        'HKLM:\SOFTWARE\WOW6432Node\Python')) {
        if (-not (Test-Path $hive)) { continue }
        foreach ($company in (Get-ChildItem $hive -ErrorAction SilentlyContinue)) {
            foreach ($tag in (Get-ChildItem $company.PSPath -ErrorAction SilentlyContinue)) {
                $install = Join-Path $tag.PSPath 'InstallPath'
                if (-not (Test-Path $install)) { continue }
                $property = Get-ItemProperty $install -ErrorAction SilentlyContinue
                if ($property.ExecutablePath) { $candidates += $property.ExecutablePath }
                elseif ($property.'(default)') {
                    $candidates += (Join-Path $property.'(default)' 'python.exe')
                }
            }
        }
    }

    foreach ($name in @('python', 'python3', 'py')) {
        $found = Get-Command $name -ErrorAction SilentlyContinue
        if ($found) { $candidates += $found.Source }
    }

    foreach ($pattern in @(
        "$env:LOCALAPPDATA\Programs\Python\Python3*\python.exe",
        "$env:LOCALAPPDATA\Microsoft\WindowsApps\python*.exe",
        "$env:ProgramFiles\Python3*\python.exe",
        "${env:ProgramFiles(x86)}\Python3*\python.exe",
        'C:\Python3*\python.exe'
    )) {
        $candidates += (Get-ChildItem -Path $pattern -ErrorAction SilentlyContinue |
                        Sort-Object FullName -Descending | ForEach-Object { $_.FullName })
    }

    return ($candidates | Where-Object { $_ } | Select-Object -Unique)
}

function Find-Python {
    param([switch] $Explain)

    $tried = @()
    foreach ($candidate in (Get-PythonCandidates)) {
        $answer = ''
        try { $answer = (& $candidate --version 2>&1 | Out-String).Trim() } catch { $answer = $_.Exception.Message }
        if ($answer -match 'Python 3') {
            if ($Explain) { Write-Host ("  {0,-60} {1}" -f $candidate, $answer) -ForegroundColor Green }
            return $candidate
        }
        $tried += ('  {0,-60} {1}' -f $candidate, $(if ($answer) { $answer } else { 'said nothing' }))
    }

    # Nothing answered. What was tried is the useful half of that.
    if ($tried) {
        Write-Host 'Looked at these and none of them answered --version with a Python 3:' -ForegroundColor Yellow
        $tried | ForEach-Object { Write-Host $_ -ForegroundColor Yellow }
    } else {
        Write-Host 'Found nothing to try: PATH has no python, python3 or py, the registry has' -ForegroundColor Yellow
        Write-Host 'no Software\Python install recorded, and the usual folders hold none.' -ForegroundColor Yellow
    }
    return $null
}
