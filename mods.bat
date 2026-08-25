@echo off
rem Double-click this to open the mod menu. Nothing else needed.
rem
rem The work is in tools\mods.py; PowerShell is here only because
rem tools\mods.ps1 already knows how to find Python on this machine - it is not
rem on PATH here, and two places searching for the same thing drift apart.
rem
rem This file is deliberately plain ASCII: cmd.exe reads a .bat in the console's
rem OEM code page, so Russian text inside a batch file arrives as mojibake. The
rem menu itself is Russian - that comes from Python, after chcp switches the
rem console to UTF-8 below.
chcp 65001 >nul
title Mods EU5
cd /d "%~dp0"

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0tools\mods.ps1" %*
set EXITCODE=%ERRORLEVEL%

echo.
if not "%EXITCODE%"=="0" (
    echo Exit code %EXITCODE%. If the error above is about Python, install it once:
    echo     winget install -e --id Python.Python.3.12
    echo.
)
pause
