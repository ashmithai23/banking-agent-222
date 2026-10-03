# Start VectraBank on Windows (PowerShell).
#   .\start.ps1          dev mode: backend (:8000) in a new window + Vite dev server (:5173)
#   .\start.ps1 prod     build the frontend and serve everything from FastAPI on :8000
# If scripts are blocked, run start.bat instead (it bypasses the execution policy).
param([string]$Mode = "dev")

$ErrorActionPreference = "Stop"
$Root = (Resolve-Path (Split-Path -Parent $MyInvocation.MyCommand.Path)).Path
# Normalize the drive letter to upper case (c:\ -> C:\); Vite on Windows can 404 on mismatched path casing
if ($Root -match '^[a-z]:') { $Root = $Root.Substring(0, 1).ToUpper() + $Root.Substring(1) }
$Backend = Join-Path $Root "backend"
$Frontend = Join-Path $Root "frontend"
$BackendPort = if ($env:BACKEND_PORT) { $env:BACKEND_PORT } else { "8000" }
$FrontendPort = if ($env:FRONTEND_PORT) { $env:FRONTEND_PORT } else { "5173" }

# Avoid UnicodeEncodeError from emoji log lines on Windows consoles
$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"

function Fail($msg) { Write-Host "ERROR: $msg" -ForegroundColor Red; exit 1 }

# --- locate Python 3.10+
$PythonCmd = $null
foreach ($candidate in @("py -3", "python", "python3")) {
    $parts = $candidate -split " "
    $exe = $parts[0]
    $extra = @($parts | Select-Object -Skip 1)
    if (Get-Command $exe -ErrorAction SilentlyContinue) {
        try {
            $ver = & $exe @extra -c "import sys; print('%d.%d' % sys.version_info[:2])" 2>$null
            if ($LASTEXITCODE -eq 0 -and $ver -and ([version]"$ver".Trim() -ge [version]"3.10")) {
                $PythonCmd = $parts
                break
            }
        } catch { }
    }
}
if (-not $PythonCmd) { Fail "Python 3.10+ not found. Install it from https://www.python.org/downloads/ (tick 'Add python.exe to PATH')." }
if (-not (Get-Command npm -ErrorAction SilentlyContinue)) { Fail "Node.js/npm not found. Install Node.js 18+ from https://nodejs.org/." }

# --- backend dependencies
Set-Location $Backend
$VenvPython = Join-Path $Backend ".venv\Scripts\python.exe"
if (-not (Test-Path $VenvPython)) {
    Write-Host ">> Creating Python virtualenv" -ForegroundColor Cyan
    $pyExe = $PythonCmd[0]
    $pyArgs = @($PythonCmd | Select-Object -Skip 1) + @("-m", "venv", ".venv")
    & $pyExe @pyArgs
    if ($LASTEXITCODE -ne 0) { Fail "Could not create the virtualenv." }
}
$Marker = Join-Path $Backend ".venv\.deps-installed"
$Req = Join-Path $Backend "requirements.txt"
if (-not (Test-Path $Marker) -or ((Get-Item $Req).LastWriteTime -gt (Get-Item $Marker).LastWriteTime)) {
    Write-Host ">> Installing backend dependencies (first run takes a few minutes)" -ForegroundColor Cyan
    & $VenvPython -m pip install --upgrade pip -q
    & $VenvPython -m pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) { Fail "pip install failed." }
    New-Item -ItemType File -Path $Marker -Force | Out-Null
}
if (-not (Test-Path (Join-Path $Backend ".env"))) {
    Copy-Item (Join-Path $Backend ".env.example") (Join-Path $Backend ".env")
}

# --- frontend dependencies
Set-Location $Frontend
if (-not (Test-Path (Join-Path $Frontend "node_modules"))) {
    Write-Host ">> Installing frontend dependencies" -ForegroundColor Cyan
    npm install --no-fund --no-audit
    if ($LASTEXITCODE -ne 0) { Fail "npm install failed." }
}

if ($Mode -eq "prod") {
    Write-Host ">> Building frontend" -ForegroundColor Cyan
    npm run build
    if ($LASTEXITCODE -ne 0) { Fail "Frontend build failed." }
    Set-Location $Backend
    Write-Host ">> Serving app at http://localhost:$BackendPort" -ForegroundColor Green
    & $VenvPython -m uvicorn api:app --host 0.0.0.0 --port $BackendPort
    exit $LASTEXITCODE
}

# --- dev mode: backend in its own window, frontend here
Write-Host ">> Starting backend in a new window (http://localhost:$BackendPort/docs)" -ForegroundColor Cyan
$backendCmd = "`$env:PYTHONUTF8='1'; `$env:PYTHONIOENCODING='utf-8'; & '$VenvPython' -m uvicorn api:app --host 0.0.0.0 --port $BackendPort"
Start-Process powershell -WorkingDirectory $Backend -ArgumentList @("-NoExit", "-ExecutionPolicy", "Bypass", "-Command", $backendCmd)

Write-Host ">> Frontend: http://localhost:$FrontendPort  (Ctrl+C to stop; close the backend window separately)" -ForegroundColor Green
$env:VITE_BACKEND_URL = "http://localhost:$BackendPort"
$env:FRONTEND_PORT = $FrontendPort
# Run Vite through node directly (PowerShell drops "--" when forwarding args via npm.ps1)
& node (Join-Path $Frontend "node_modules\vite\bin\vite.js")
