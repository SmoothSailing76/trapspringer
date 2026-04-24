from trapspringer.layers.layer10_audit.service import AuditReplayService

def test_audit_service_snapshot():
    svc = AuditReplayService()
    snap = svc.create_snapshot("start")
    assert snap.startswith("SNAP-")
