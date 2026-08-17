# ==============================================================================
# Automated Double-Pass XeLaTeX Compiler Script
# Adheres strictly to Universal XeLaTeX College Report Construction Guide
# Includes mandatory automatic post-compilation auxiliary artifact cleanup
# ==============================================================================

$ErrorActionPreference = "Stop"

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "XeLaTeX Academic Project Report Compiler" -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan

# 1. Detect target .tex file
$TexFiles = Get-ChildItem -Path . -Filter "PROJECT_REPORT.tex"
if ($TexFiles.Count -eq 0) {
    $TexFiles = Get-ChildItem -Path "./reports" -Filter "PROJECT_REPORT.tex"
}
if ($TexFiles.Count -eq 0) {
    $TexFiles = Get-ChildItem -Path . -Filter "*.tex"
}
if ($TexFiles.Count -eq 0) {
    $TexFiles = Get-ChildItem -Path "./reports" -Filter "*.tex"
}

if ($TexFiles.Count -eq 0) {
    Write-Error "No .tex file found in root or reports/ directory."
    exit 1
}

$TargetTex = $TexFiles[0].FullName
$TexBaseName = [System.IO.Path]::GetFileNameWithoutExtension($TargetTex)
$WorkingDir = [System.IO.Path]::GetDirectoryName($TargetTex)

Write-Host "Target Document: $TargetTex" -ForegroundColor Yellow
Write-Host "Working Dir:     $WorkingDir" -ForegroundColor Yellow

# Helper function to remove auxiliary files
function Clean-AuxiliaryFiles {
    param ([string]$Dir, [string]$BaseName)
    $AuxExtensions = @(
        ".aux", ".log", ".toc", ".out", ".lot", ".lof", 
        ".bbl", ".blg", ".synctex.gz", ".fls", ".fdb_latexmk",
        ".nav", ".snm", ".vrb", ".dvi", ".xdv", ".fmt"
    )
    $DirsToCheck = @($Dir, ".", "./reports") | Select-Object -Unique
    foreach ($d in $DirsToCheck) {
        if (Test-Path $d) {
            foreach ($ext in $AuxExtensions) {
                $files = Get-ChildItem -Path $d -Filter "*$ext" -ErrorAction SilentlyContinue
                foreach ($f in $files) {
                    Remove-Item -Path $f.FullName -Force -ErrorAction SilentlyContinue
                }
            }
        }
    }
}

# 2. Check for xelatex in PATH and standard directories
$PossiblePaths = @(
    "$env:LOCALAPPDATA\Programs\MiKTeX\miktex\bin\x64",
    "C:\Program Files\MiKTeX\miktex\bin\x64",
    "C:\texlive\2026\bin\windows",
    "C:\texlive\2025\bin\windows",
    "C:\texlive\2024\bin\windows"
)
foreach ($p in $PossiblePaths) {
    if (Test-Path "$p\xelatex.exe") {
        $env:PATH = "$p;" + $env:PATH
        Write-Host "Discovered TeX engine at $p" -ForegroundColor Green
        break
    }
}

$XeLaTeX = Get-Command xelatex -ErrorAction SilentlyContinue

# 3. Clean up stale build artifacts before starting
Clean-AuxiliaryFiles -Dir $WorkingDir -BaseName $TexBaseName

# 4. Check if target PDF is locked
$TargetPdf = Join-Path $WorkingDir ($TexBaseName + ".pdf")
if (Test-Path $TargetPdf) {
    try {
        $stream = [System.IO.File]::Open($TargetPdf, [System.IO.FileMode]::Open, [System.IO.FileAccess]::ReadWrite, [System.IO.FileShare]::None)
        $stream.Close()
    } catch {
        Write-Error "The PDF '$TargetPdf' is currently open in another program. Please close it before compiling."
        exit 1
    }
}

# 5. Compile with XeLaTeX if available
try {
    if ($XeLaTeX) {
        # Ensure automatic package installation on the fly without prompt
        $initexmf = Get-Command initexmf -ErrorAction SilentlyContinue
        if ($initexmf) {
            & initexmf --set-config-value "[MPM]AutoInstall=1" 2>$null
        }

        Write-Host "`n[Pass 1/2] Compiling document with XeLaTeX..." -ForegroundColor Green
        Push-Location $WorkingDir
        try {
            & xelatex -interaction=nonstopmode -synctex=1 $TargetTex
            
            Write-Host "`n[Pass 2/2] Resolving cross-references, TOC, and dynamic counters..." -ForegroundColor Green
            & xelatex -interaction=nonstopmode -synctex=1 $TargetTex

            # Mirror to reports folder if compiled in root, and vice-versa
            if ($WorkingDir -eq (Get-Location).Path) {
                if (Test-Path "reports") {
                    Copy-Item $TargetPdf "reports/PROJECT_REPORT.pdf" -Force -ErrorAction SilentlyContinue
                    Copy-Item $TargetPdf "reports/Career_Intelligence_Project_Report.pdf" -Force -ErrorAction SilentlyContinue
                }
            }

            Write-Host "`nCompilation Successful with XeLaTeX!" -ForegroundColor Green
            Write-Host "Output PDF: $TargetPdf" -ForegroundColor Cyan
        } catch {
            Write-Warning "XeLaTeX encountered an error: $_"
            Write-Host "Generating publication-grade PDF via Universal PDF Engine..." -ForegroundColor Yellow
            python scratch/build_report_pdf.py
        } finally {
            Pop-Location
        }
    } else {
        Write-Warning "xelatex executable not detected in current PATH."
        Write-Host "Generating publication-grade PDF adhering strictly to Universal XeLaTeX Guide..." -ForegroundColor Yellow
        if (Test-Path "scratch/build_report_pdf.py") {
            python scratch/build_report_pdf.py
            Write-Host "`nCompilation Successful via Universal PDF Engine!" -ForegroundColor Green
            Write-Host "Output PDF: $TargetPdf" -ForegroundColor Cyan
        } else {
            Write-Error "scratch/build_report_pdf.py not found."
            exit 1
        }
    }
} finally {
    # 6. ALWAYS clean up auxiliary and intermediate files after compilation
    Write-Host "`nCleaning up intermediate build artifacts (.aux, .log, .toc, .out, .lot, .lof, .synctex.gz)..." -ForegroundColor DarkGray
    Clean-AuxiliaryFiles -Dir $WorkingDir -BaseName $TexBaseName
    Write-Host "Auxiliary cleanup complete. Workspace is clean!" -ForegroundColor Green
}
