# rules/squat_rules.py 

# CAPA DE RAZONAMIENTO - MOTOR DE REGLAS BIOMECANICAS

# Contiene las 4 reglas biomecanicas del squat: produndidad de rodilla, inclinacion del 
# trono, valfo de rodilla y asimetria bilateral. Cada regla es una funcion pura que recibe
# angulos y retorna un Finding. La funcion analyze_squat() ejectua todas las reglas
# y agruga los resultados

# rules/squat_rules.py
# rules/squat_rules.py
from .base_rules import Finding, Severity, AnalysisResult
from config import SQUAT


def check_squat_depth(angles: dict) -> Finding:
    knee = angles["avg_knee"]
    print(f"RULE CHECK — knee={knee:.1f}  boundaries: <{SQUAT['knee_angle_too_deep']} | {SQUAT['knee_angle_depth_perfect_min']}-{SQUAT['knee_angle_depth_perfect_max']} | >{SQUAT['knee_angle_too_shallow']}")

    if knee < SQUAT["knee_angle_too_deep"]:
        return Finding(
            "squat_depth", Severity.ERROR,
            f"Too deep ({knee:.0f}°)",
            "Too deep! Rise up slightly — protect your knees",
            value=knee
        )

    elif knee < SQUAT["knee_angle_depth_perfect_min"]:
        return Finding(
            "squat_depth", Severity.WARNING,
            f"Slightly too deep ({knee:.0f}°)",
            "Rise up just slightly",
            value=knee
        )

    elif knee <= SQUAT["knee_angle_depth_perfect_max"]:
        return Finding(
            "squat_depth", Severity.OK,
            f"Perfect depth ({knee:.0f}°)",
            "Perfect depth — hold this position",
            value=knee
        )

    elif knee <= SQUAT["knee_angle_too_shallow"]:
        return Finding(
            "squat_depth", Severity.WARNING,
            f"Almost there ({knee:.0f}°)",
            "Almost — go just a bit deeper",
            value=knee
        )

    else:
        return Finding(
            "squat_depth", Severity.ERROR,
            f"Not deep enough ({knee:.0f}°)",
            "Go deeper — aim for 85° to 95°",
            value=knee
        )

def check_foot_position(angles: dict) -> Finding:
    ratio = angles["foot_shoulder_ratio"]

    if ratio < SQUAT["foot_shoulder_ratio_min"]:
        return Finding(
            "foot_position", Severity.ERROR,
            f"Pies muy juntos (ratio {ratio:.2f})",
            "Abre más los pies — deben estar al ancho de tus hombros",
            value=ratio
        )

    elif ratio > SQUAT["foot_shoulder_ratio_max"]:
        return Finding(
            "foot_position", Severity.ERROR,
            f"Pies muy abiertos (ratio {ratio:.2f})",
            "Cierra un poco los pies — deben estar al ancho de tus hombros",
            value=ratio
        )

    else:
        return Finding(
            "foot_position", Severity.OK,
            f"Posición de pies correcta (ratio {ratio:.2f})",
            "Buena posición de pies",
            value=ratio
        )

def check_trunk_lean(angles: dict) -> Finding:
    lean = angles["trunk_lean"]
    if lean <= SQUAT["trunk_lean_max"]:
        return Finding(
            "trunk_lean", Severity.OK,
            f"Trunk angle OK ({lean:.0f}°)",
            "Good torso position",
            value=lean
        )
    else:
        return Finding(
            "trunk_lean", Severity.ERROR,
            f"Excessive forward lean ({lean:.0f}°)",
            "Chest up! Brace your core and keep your torso upright",
            value=lean
        )


def check_knee_valgus(angles: dict) -> Finding:
    ratio = angles["knee_valgus_ratio"]
    if ratio >= SQUAT["knee_valgus_ratio_min"]:
        return Finding(
            "knee_valgus", Severity.OK,
            "Knee tracking good",
            "Knees tracking over toes",
            value=ratio
        )
    else:
        return Finding(
            "knee_valgus", Severity.ERROR,
            f"Knee valgus detected (ratio {ratio:.2f})",
            "Push your knees OUT — drive them in line with your toes",
            value=ratio
        )


def check_asymmetry(angles: dict) -> Finding:
    diff = abs(angles["left_knee"] - angles["right_knee"])
    if diff <= 15:
        return Finding(
            "asymmetry", Severity.OK,
            f"Symmetric ({diff:.0f}° diff)",
            "Good bilateral symmetry",
            value=diff
        )
    else:
        return Finding(
            "asymmetry", Severity.WARNING,
            f"Left/right asymmetry ({diff:.0f}° diff)",
            "Check for uneven weight distribution between legs",
            value=diff
        )


SQUAT_RULES = [
    check_squat_depth,
    check_trunk_lean,
    check_knee_valgus,
    check_asymmetry,
    check_foot_position,   # ← nuevo
]


def analyze_squat(angles: dict, phase: str = "unknown") -> AnalysisResult:
    result = AnalysisResult(exercise="squat", phase=phase)
    for rule_fn in SQUAT_RULES:
        result.findings.append(rule_fn(angles))
    return result