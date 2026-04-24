from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

from .loader import load_scenario_directory, load_scenario_script
from .models import SUPPORTED_HOOKS, SUPPORTED_OPS, ScenarioScript

@dataclass(slots=True)
class ScenarioValidationReport:
    checked_scripts: int = 0
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors

    def to_dict(self) -> dict:
        return {"ok": self.ok, "checked_scripts": self.checked_scripts, "errors": self.errors, "warnings": self.warnings}

def validate_script(script: ScenarioScript) -> ScenarioValidationReport:
    report = ScenarioValidationReport(checked_scripts=1)
    if not script.script_id:
        report.errors.append("script id is required")
    used_steps = 0
    for hook in SUPPORTED_HOOKS:
        steps = script.steps_for_hook(hook)
        used_steps += len(steps)
        for idx, step in enumerate(steps, start=1):
            if step.op not in SUPPORTED_OPS:
                report.errors.append(f"{script.script_id}.{hook}[{idx}] unsupported op: {step.op}")
            if step.when is not None and not isinstance(step.when, dict):
                report.errors.append(f"{script.script_id}.{hook}[{idx}] when must be an object")
    if used_steps == 0:
        report.warnings.append(f"{script.script_id} has no executable steps")
    return report

def merge_reports(reports: Iterable[ScenarioValidationReport]) -> ScenarioValidationReport:
    merged = ScenarioValidationReport()
    for report in reports:
        merged.checked_scripts += report.checked_scripts
        merged.errors.extend(report.errors)
        merged.warnings.extend(report.warnings)
    return merged

def validate_script_path(path: str | Path) -> ScenarioValidationReport:
    p = Path(path)
    if p.is_dir():
        return merge_reports(validate_script(script) for script in load_scenario_directory(p))
    return validate_script(load_scenario_script(p))
