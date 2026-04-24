from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from trapspringer.scenario_dsl.validator import validate_script_path
from .service import ContentPackService

@dataclass(slots=True)
class ContentPackValidationReport:
    pack_id: str
    ok: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    resource_count: int = 0
    script_count: int = 0

    def to_dict(self) -> dict:
        return {"pack_id": self.pack_id, "ok": self.ok, "errors": self.errors, "warnings": self.warnings, "resource_count": self.resource_count, "script_count": self.script_count}

def validate_content_pack(pack_id: str = "dl1_dragons_of_despair", packs_root: str | Path | None = None) -> ContentPackValidationReport:
    service = ContentPackService(packs_root)
    manifest = service.get(pack_id)
    errors: list[str] = []
    warnings: list[str] = []
    script_count = 0
    for rid, resource in manifest.resources.items():
        path = manifest.resource_path(rid)
        if not path.exists():
            errors.append(f"missing resource {rid}: {path}")
            continue
        if resource.kind == "scenario_script":
            report = validate_script_path(path)
            script_count += report.checked_scripts
            errors.extend(f"{rid}: {e}" for e in report.errors)
            warnings.extend(f"{rid}: {w}" for w in report.warnings)
    if not manifest.rules_capabilities:
        warnings.append("content pack does not declare rules_capabilities")
    if not manifest.main_path_registry:
        warnings.append("content pack does not declare main_path_registry")
    return ContentPackValidationReport(pack_id=manifest.pack_id, ok=not errors, errors=errors, warnings=warnings, resource_count=len(manifest.resources), script_count=script_count)
