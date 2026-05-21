# rules/deadlift_rules.py

# CAPA DE RAZONAMIENTO - MOTOR DE REGLAS BIOMECANICAS

# Contiene las 3 reglas biomecanicas del deadlift: redondeo de espalda, angulo de rodilla en el setup y 
# postura del cuello. Mismo patron que el modulo de squat - extensible para agregar mas reglas sin 
# modificar el agente

from .base_rules import Finding, Severity, AnalysisResult
from config import DEADLIFT


def check_back_rounding(angles: dict) -> Finding:
    angle = angles["back_angle"]
    if angle <= DEADLIFT["back_angle_max"]:
        return Finding("back_rounding", Severity.OK,
                       f"Back angle OK ({angle:.0f}°)",
                       "Maintain neutral spine throughout the lift", value=angle)
    else:
        return Finding("back_rounding", Severity.ERROR,
                       f"Back rounding detected ({angle:.0f}°)",
                       "Hinge at the hips — brace your core and keep a neutral spine", value=angle)


def check_deadlift_knee(angles: dict) -> Finding:
    angle = angles["knee_angle"]
    if angle >= DEADLIFT["knee_angle_min"]:
        return Finding("deadlift_knee", Severity.OK,
                       f"Knee angle OK ({angle:.0f}°)",
                       "Good starting position", value=angle)
    else:
        return Finding("deadlift_knee", Severity.WARNING,
                       f"Low knee angle ({angle:.0f}°)",
                       "Drive through your heels and push the floor away", value=angle)


def check_neck_alignment(angles: dict) -> Finding:
    angle = angles["neck_angle"]
    if angle <= DEADLIFT["neck_angle_max"]:
        return Finding("neck_alignment", Severity.OK,
                       f"Neck neutral ({angle:.0f}°)",
                       "Good head position", value=angle)
    else:
        return Finding("neck_alignment", Severity.WARNING,
                       f"Forward head posture ({angle:.0f}°)",
                       "Keep your gaze about 1 metre ahead — neutral neck", value=angle)


DEADLIFT_RULES = [
    check_back_rounding,
    check_deadlift_knee,
    check_neck_alignment,
]


def analyze_deadlift(angles: dict, phase: str = "unknown") -> AnalysisResult:
    result = AnalysisResult(exercise="deadlift", phase=phase)
    for rule_fn in DEADLIFT_RULES:
        result.findings.append(rule_fn(angles))
    return result