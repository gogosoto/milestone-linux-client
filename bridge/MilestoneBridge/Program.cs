using Grpc.Core;
using MilestoneBridge;
using VideoOS.Platform;
using VideoOS.Platform.SDK;
using VideoOS.Platform.Messaging;

namespace MilestoneBridgeService;

/// <summary>
/// Thin gRPC server that wraps the Milestone VideoOS.Platform.SDK
/// for features not available via REST/WebRTC/Mobile protocols.
/// 
/// Deploy on any Windows machine with access to the XProtect Recording Server.
/// Start with: dotnet run --urls http://0.0.0.0:50051
/// </summary>
public class Program
{
    public static void Main(string[] args)
    {
        var builder = WebApplication.CreateBuilder(args);
        builder.Services.AddGrpc();
        var app = builder.Build();
        app.MapGrpcService<BridgeServiceImpl>();
        app.Run();
    }
}

public class BridgeServiceImpl : MilestoneBridge.MilestoneBridgeBase
{
    private readonly ILogger<BridgeServiceImpl> _logger;

    public BridgeServiceImpl(ILogger<BridgeServiceImpl> logger)
    {
        _logger = logger;
    }

    // ── Connection helper ────────────────────────────────────────────

    private static void InitializeSdk()
    {
        if (!Environment.UserInteractive)
            VideoOS.Platform.SDK.Environment.Initialize();
    }

    private static ServerSession CreateSession(string serverUrl, string username, string password)
    {
        var uri = new Uri(serverUrl);
        var session = new ServerSession(uri, username, password, ServerSession.LoginMethod.Basic);
        session.Connect();
        return session;
    }

    // ── Smart Search ─────────────────────────────────────────────────

    public override Task<MotionSearchResult> StartMotionSearch(
        MotionSearchRequest request, ServerCallContext context)
    {
        _logger.LogInformation("SmartSearch: camera={CameraId} range={Start}-{End}",
            request.CameraId, request.StartTime, request.EndTime);

        // TODO: Use VideoOS.Platform.SDK.Playback.SmartSearchSession
        return Task.FromResult(new MotionSearchResult
        {
            TaskId = Guid.NewGuid().ToString(),
            Started = true
        });
    }

    public override Task<ProgressResponse> GetMotionSearchProgress(
        ProgressRequest request, ServerCallContext context)
    {
        return Task.FromResult(new ProgressResponse { Progress = 100 });
    }

    // ── Evidence Lock ────────────────────────────────────────────────

    public override Task<EvidenceResponse> LockEvidence(
        EvidenceRequest request, ServerCallContext context)
    {
        // TODO: Use VideoOS.Platform.SDK.Export.EvidenceLock
        return Task.FromResult(new EvidenceResponse
        {
            Success = true,
            EvidenceId = Guid.NewGuid().ToString()
        });
    }

    public override Task<EvidenceResponse> UnlockEvidence(
        EvidenceRequest request, ServerCallContext context)
    {
        return Task.FromResult(new EvidenceResponse { Success = true });
    }

    public override Task<EvidenceListResponse> GetLockedEvidence(
        EvidenceListRequest request, ServerCallContext context)
    {
        return Task.FromResult(new EvidenceListResponse());
    }

    // ── Privacy Masking ─────────────────────────────────────────────

    public override Task<RestrictedMediaResponse> GetRestrictedMedia(
        RestrictedMediaRequest request, ServerCallContext context)
    {
        return Task.FromResult(new RestrictedMediaResponse { HasRestrictions = false });
    }

    // ── Hardware Management ─────────────────────────────────────────

    public override Task<HardwareScanResponse> ScanHardware(
        HardwareScanRequest request, ServerCallContext context)
    {
        _logger.LogInformation("HardwareScan: range={Range} recorder={RecorderId}",
            request.IpRange, request.RecordingServerId);
        // TODO: Use RecordingServer.HardwareScanExpress()
        return Task.FromResult(new HardwareScanResponse());
    }

    public override Task<HardwareAddResponse> AddHardware(
        HardwareAddRequest request, ServerCallContext context)
    {
        _logger.LogInformation("AddHardware: IP={Ip} name={Name} driver={Driver}",
            request.Ip, request.HardwareName, request.DriverId);
        return Task.FromResult(new HardwareAddResponse
        {
            Success = true,
            HardwareId = Guid.NewGuid().ToString()
        });
    }

    public override Task<Empty> RemoveHardware(
        HardwareRemoveRequest request, ServerCallContext context)
    {
        return Task.FromResult(new Empty());
    }

    public override Task<FirmwareResponse> FirmwareUpdate(
        FirmwareRequest request, ServerCallContext context)
    {
        return Task.FromResult(new FirmwareResponse { Success = true });
    }

    // ── System ──────────────────────────────────────────────────────

    public override Task<LogResponse> GetSystemLogs(
        LogQuery request, ServerCallContext context)
    {
        // TODO: Read from Management Server event log
        return Task.FromResult(new LogResponse());
    }

    public override Task<SystemStatusResponse> GetSystemStatus(
        Empty request, ServerCallContext context)
    {
        return Task.FromResult(new SystemStatusResponse
        {
            Status = "OK",
            CpuUsage = 0,
            MemoryUsage = 0,
            DiskUsage = 0,
            ActiveSessions = 0
        });
    }

    public override Task<RecordingServerStatus> GetRecordingServerStatus(
        Empty request, ServerCallContext context)
    {
        return Task.FromResult(new RecordingServerStatus { Status = "OK" });
    }

    // ── Video Wall ──────────────────────────────────────────────────

    public override Task<VideoWallList> GetVideoWalls(
        Empty request, ServerCallContext context)
    {
        return Task.FromResult(new VideoWallList());
    }

    public override Task<Empty> SendToVideoWall(
        VideoWallCommand request, ServerCallContext context)
    {
        return Task.FromResult(new Empty());
    }

    // ── PTZ Patrols ─────────────────────────────────────────────────

    public override Task<PatrolList> GetPatrols(
        PatrolQuery request, ServerCallContext context)
    {
        return Task.FromResult(new PatrolList());
    }

    public override Task<Empty> StartPatrol(
        PatrolCommand request, ServerCallContext context)
    {
        return Task.FromResult(new Empty());
    }

    public override Task<Empty> StopPatrol(
        PatrolCommand request, ServerCallContext context)
    {
        return Task.FromResult(new Empty());
    }
}
