@echo off
REM Deploy the Windows .NET Bridge to a remote Windows machine
REM Usage: deploy_bridge.ps1 -ComputerName RECORDING-SERVER -Destination C:\MilestoneBridge

set COMPUTER=%1
set DEST=%2

if "%COMPUTER%"=="" (
    echo Usage: %0 COMPUTER_NAME [DEST_PATH]
    echo Example: %0 RECORDING-SERVER C:\MilestoneBridge
    exit /b 1
)

if "%DEST%"=="" set DEST=C:\MilestoneBridge

echo Building bridge...
dotnet publish ..\bridge\MilestoneBridge -r win-x64 --self-contained -o build\bridge

echo Copying to %COMPUTER%:%DEST%...
xcopy /E /I /Y build\bridge "\\%COMPUTER%\%DEST%"

echo Installing as Windows service...
sc \\%COMPUTER% create MilestoneBridge binPath="%DEST%\MilestoneBridge.exe --urls http://0.0.0.0:50051"
sc \\%COMPUTER% start MilestoneBridge

echo Bridge deployed successfully.
echo Linux client should connect to %COMPUTER%:50051
