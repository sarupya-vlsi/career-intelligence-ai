# ==============================================================================
# Automated Double-Pass XeLaTeX Compiler Script
# Adheres strictly to Universal XeLaTeX College Report Construction Guide
# Includes mandatory automatic post-compilation auxiliary artifact cleanup
# ==============================================================================

$ErrorActionPreference = "Stop"

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "XeLaTeX Academic Research Paper & Technical Report Compiler" -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan

$ScriptRoot = $PSScriptRoot
if (-not $ScriptRoot) {
    $ScriptRoot = (Get-Location).Path
}

# 1. Detect target .tex file (Prioritize reports/RESEARCH_PAPER.tex, then root)
$TargetTex = $null
if (Test-Path "$ScriptRoot\reports\RESEARCH_PAPER.tex") {
    $TargetTex = "$ScriptRoot\reports\RESEARCH_PAPER.tex"
} elseif (Test-Path "$ScriptRoot\RESEARCH_PAPER.tex") {
    $TargetTex = "$ScriptRoot\RESEARCH_PAPER.tex"
} else {
    $found = Get-ChildItem -Path $ScriptRoot -Recurse -Filter "*.tex" | Where-Object { $_.FullName -notmatch "\\.git" }
    if ($found.Count -gt 0) {
        $TargetTex = $found[0].FullName
    }
}

if (-not $TargetTex -or -not (Test-Path $TargetTex)) {
    Write-Error "No .tex file found in workspace."
    exit 1
}

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
    $DirsToCheck = @($Dir, $ScriptRoot, "$ScriptRoot\reports") | Select-Object -Unique
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
        } finally {
            Pop-Location
        }

        # Mirror PDF between root and reports/
        $RootPdf = Join-Path $ScriptRoot "RESEARCH_PAPER.pdf"
        $ReportsPdf = Join-Path $ScriptRoot "reports\RESEARCH_PAPER.pdf"
        
        if (Test-Path $ReportsPdf) {
            Copy-Item $ReportsPdf $RootPdf -Force -ErrorAction SilentlyContinue
        } elseif (Test-Path $RootPdf) {
            Copy-Item $RootPdf $ReportsPdf -Force -ErrorAction SilentlyContinue
        }

        Write-Host "`nCompilation Successful with XeLaTeX!" -ForegroundColor Green
        Write-Host "Output PDF: $TargetPdf" -ForegroundColor Cyan
    } else {
        Write-Error "xelatex executable not detected in current PATH or standard locations."
        exit 1
    }
} finally {
    # 6. ALWAYS clean up auxiliary and intermediate files after compilation
    Write-Host "`nCleaning up intermediate build artifacts (.aux, .log, .toc, .out, .lot, .lof, .synctex.gz)..." -ForegroundColor DarkGray
    Clean-AuxiliaryFiles -Dir $WorkingDir -BaseName $TexBaseName
    Write-Host "Auxiliary cleanup complete. Workspace is clean!" -ForegroundColor Green
}
