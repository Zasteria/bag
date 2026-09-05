# 1. Define Target Paths (User Desktop and Steam Workshop)
$TargetPaths = @(
    "C:\Users\Siermayde",
    "C:\Program Files (x86)\Steam\steamapps\workshop"
)

Write-Host "=== STARTING NUL FILE CLEANUP ===" -ForegroundColor Cyan
Write-Host "Scanning directories... (This may take a while)" -ForegroundColor Gray

foreach ($Path in $TargetPaths) {
    if (Test-Path $Path) {
        Write-Host "Scanning folder: $Path" -ForegroundColor Yellow
        
        # Recursive search for "nul" files
        # Using ErrorAction SilentlyContinue to skip permission errors
        $Files = Get-ChildItem -Path $Path -Recurse -Force -ErrorAction SilentlyContinue | Where-Object { $_.Name -eq "nul" }
        
        foreach ($File in $Files) {
            $FullPath = $File.FullName
            Write-Host "FOUND TARGET: $FullPath" -ForegroundColor Red
            
            # Use UNC path prefix \\.\ to force delete
            $UNCPath = "\\.\$FullPath"
            
            # Execute CMD delete command
            cmd /c "del /f /q `"$UNCPath`""
            
            # Verify deletion
            if (Test-Path $FullPath) {
                Write-Host "  [FAILED] Could not delete (File locked?)" -ForegroundColor DarkRed
            } else {
                Write-Host "  [SUCCESS] DELETED!" -ForegroundColor Green
            }
        }
    } else {
        Write-Host "Directory not found: $Path" -ForegroundColor DarkGray
    }
}

Write-Host "`n=== CLEANUP FINISHED ===" -ForegroundColor Cyan
Write-Host "Press Enter to exit..."
Read-Host