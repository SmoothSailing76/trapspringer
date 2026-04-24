class SnapshotService:
    def autosave(self, audit_service, label: str | None = None, state: dict | None = None):
        return audit_service.create_snapshot(label=label, state=state)
