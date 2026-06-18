# Milestone Linux Client Bridge

.NET 8 gRPC server that wraps Milestone's `VideoOS.Platform.SDK` (Windows only)
for features not available via REST/WebRTC/Mobile protocols.

## Prerequisites

- Windows machine (Recording Server or standalone)
- .NET 8 SDK
- Access to XProtect VMS

## Build

```powershell
cd bridge/MilestoneBridge
dotnet restore
dotnet build
```

## Deploy

Copy the built binary to the Windows machine. Start the bridge:

```powershell
MilestoneBridge.exe --urls http://0.0.0.0:50051
```

For production, run as a Windows Service:

```powershell
sc create MilestoneBridge binPath="C:\path\to\MilestoneBridge.exe --urls http://0.0.0.0:50051"
sc start MilestoneBridge
```

## Features Exposed

| gRPC Method | SDK Feature Used |
|------------|-----------------|
| StartMotionSearch | `VideoOS.Platform.SDK.Playback.SmartSearchSession` |
| LockEvidence | `VideoOS.Platform.SDK.Export.EvidenceLock` |
| ScanHardware | `RecordingServer.HardwareScanExpress()` |
| AddHardware | `RecordingServer.AddHardware()` |
| GetSystemLogs | Management Server event log |
| GetVideoWalls | Matrix/Monitor configuration |
| GetPatrols | PTZ patrol configuration |
