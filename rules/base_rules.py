# rules/base_rules.py

# CAPA DE RAZONAMIENTO - MOTOR DE REGLAS BIOMECANICAS

# Define las estructuas de datos compartidas por todo el motore de reglas
# Severity (OK/WARNING/ERROR), Finding (un hallazgo individual con severidad, 
# mensaje y cue de coaching), y AnalysisResult (coleccion de findings con 
# prioridades convenientes como .errors y .worst_severity).

from dataclasses import dataclass, field
from enum import Enum


class Severity(Enum):
    OK      = "ok"
    WARNING = "warning"
    ERROR   = "error"


@dataclass
class Finding:
    rule:     str
    severity: Severity
    message:  str
    cue:      str        # the coaching instruction shown to the user
    value:    float = 0.0


@dataclass
class AnalysisResult:
    exercise: str
    phase:    str = "unknown"
    findings: list[Finding] = field(default_factory=list)

    @property
    def errors(self):
        return [f for f in self.findings if f.severity == Severity.ERROR]

    @property
    def warnings(self):
        return [f for f in self.findings if f.severity == Severity.WARNING]

    @property
    def worst_severity(self) -> Severity:
        if self.errors:   return Severity.ERROR
        if self.warnings: return Severity.WARNING
        return Severity.OK