@echo off
title NOVA AI — localsite + link
cd /d "%~dp0"

echo ============================================================
echo  NOVA AI — local server + Cloudflare link
echo  Keep this window OPEN while you want the link to work.
echo ============================================================
echo.

rem --- start the local server (silently, if not already running) ---
powershell -NoProfile -Command "if (-not (Get-NetTCPConnection -LocalPort 8756 -State Listen -ErrorAction SilentlyContinue)) { Start-Process python -ArgumentList '-m','http.server','8756','--bind','0.0.0.0' -WorkingDirectory '%~dp0' -WindowStyle Minimized }"
timeout /t 2 /nobreak >nul

echo Local server : http://localhost:8756  (check port 8756)
echo.
echo Starting Cloudflare tunnel... your public link appears below.
echo Copy it to your phone / send it to anyone - works from any network.
echo Closing this window stops the link.
echo.

if not exist "%LOCALAPPDATA%\opencode\cloudflared.exe" (
  echo ERROR: cloudflared.exe not found in %LOCALAPPDATA%\opencode
  pause
  exit /b 1
)

"%LOCALAPPDATA%\opencode\cloudflared.exe" tunnel --url http://localhost:8756 --protocol http2 --no-autoupdate

pause