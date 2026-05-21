# angles.py

# CAPA DE PERCEPCION - CAPA SENSORIAL DEL AGENTE

# Convierte landmarks crudos en angulos articulares significativos usando geometria
# vectorial (producto punto + arcos). Calcula angulo de rodilla izquierda/derecha, 
# inclinacion del tronco, angulos de cadera y ratio de valgo de rodilla para el
# squat; y angulo de espalda, rodillo y cuello para el deadlift. Retorna None si
# algun landmark clave no es visible

import numpy as np
from pose import LM
from config import LANDMARK_VISIBILITY_THRESHOLD


def angle_between(a: np.ndarray, b: np.ndarray, c: np.ndarray) -> float:
    """Angle in degrees at joint B formed by vectors B→A and B→C (2D)."""
    ba = a[:2] - b[:2]
    bc = c[:2] - b[:2]
    cos_val = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc) + 1e-9)
    return float(np.degrees(np.arccos(np.clip(cos_val, -1.0, 1.0))))


def is_visible(lm: dict, *indices) -> bool:
    return all(
        lm.get(i, np.zeros(4))[3] >= LANDMARK_VISIBILITY_THRESHOLD
        for i in indices
    )


def compute_squat_angles(lm: dict) -> dict | None:
    needed = [
        LM.LEFT_HIP,   LM.LEFT_KNEE,   LM.LEFT_ANKLE,
        LM.RIGHT_HIP,  LM.RIGHT_KNEE,  LM.RIGHT_ANKLE,
        LM.LEFT_SHOULDER, LM.RIGHT_SHOULDER,
    ]
    if not is_visible(lm, *needed):
        return None

    l_hip    = lm[LM.LEFT_HIP]
    l_knee   = lm[LM.LEFT_KNEE]
    l_ankle  = lm[LM.LEFT_ANKLE]
    r_hip    = lm[LM.RIGHT_HIP]
    r_knee   = lm[LM.RIGHT_KNEE]
    r_ankle  = lm[LM.RIGHT_ANKLE]
    l_sho    = lm[LM.LEFT_SHOULDER]
    r_sho    = lm[LM.RIGHT_SHOULDER]

    # ── Foot positioning ────────────────────────────────────────
    l_ankle = lm[LM.LEFT_ANKLE]
    r_ankle = lm[LM.RIGHT_ANKLE]

    shoulder_width = abs(l_sho[0] - r_sho[0])
    foot_width     = abs(l_ankle[0] - r_ankle[0])
    foot_shoulder_ratio = foot_width / (shoulder_width + 1e-9)

    l_knee_angle = angle_between(l_hip,  l_knee, l_ankle)
    r_knee_angle = angle_between(r_hip,  r_knee, r_ankle)

    mid_sho  = (l_sho[:2]  + r_sho[:2])  / 2
    mid_hip  = (l_hip[:2]  + r_hip[:2])  / 2
    mid_knee = (l_knee[:2] + r_knee[:2]) / 2

    sho_pt   = np.array([mid_sho[0],  mid_sho[1],  0, 1.0])
    hip_pt   = np.array([mid_hip[0],  mid_hip[1],  0, 1.0])
    knee_pt  = np.array([mid_knee[0], mid_knee[1], 0, 1.0])

    hip_angle  = angle_between(sho_pt, hip_pt, knee_pt)

    spine_vec  = mid_sho - mid_hip
    vertical   = np.array([0.0, -1.0])
    cos_t      = np.dot(spine_vec, vertical) / (np.linalg.norm(spine_vec) + 1e-9)
    trunk_lean = float(np.degrees(np.arccos(np.clip(cos_t, -1.0, 1.0))))

    knee_width        = abs(l_knee[0] - r_knee[0])
    ankle_width       = abs(l_ankle[0] - r_ankle[0])
    knee_valgus_ratio = knee_width / (ankle_width + 1e-9)

    return {
    "left_knee":           l_knee_angle,
    "right_knee":          r_knee_angle,
    "avg_knee":            (l_knee_angle + r_knee_angle) / 2,
    "hip_angle":           hip_angle,
    "trunk_lean":          trunk_lean,
    "knee_valgus_ratio":   knee_valgus_ratio,
    "foot_shoulder_ratio": foot_shoulder_ratio,   # ← nuevo
    "shoulder_width":      shoulder_width,         # ← nuevo
    "foot_width":          foot_width,             # ← nuevo
    "kp_left_knee":        l_knee,
    "kp_right_knee":       r_knee,
    "kp_left_hip":         l_hip,
    "kp_right_hip":        r_hip,
    "kp_mid_hip":          hip_pt,
    "kp_left_ankle":       l_ankle,               # ← nuevo
    "kp_right_ankle":      r_ankle,               # ← nuevo
    "kp_left_shoulder":    l_sho,                 # ← nuevo
    "kp_right_shoulder":   r_sho,                 # ← nuevo
}


def compute_deadlift_angles(lm: dict) -> dict | None:
    needed = [
        LM.LEFT_HIP, LM.LEFT_KNEE, LM.LEFT_ANKLE,
        LM.LEFT_SHOULDER, LM.LEFT_EAR,
    ]
    if not is_visible(lm, *needed):
        return None

    hip  = lm[LM.LEFT_HIP]
    knee = lm[LM.LEFT_KNEE]
    ankle= lm[LM.LEFT_ANKLE]
    sho  = lm[LM.LEFT_SHOULDER]
    ear  = lm[LM.LEFT_EAR]

    knee_angle = angle_between(hip, knee, ankle)
    horiz_ref  = np.array([hip[0] + 100, hip[1], 0, 1.0])
    back_angle = angle_between(sho, hip, horiz_ref)
    neck_angle = angle_between(ear, sho, hip)

    return {
        "knee_angle": knee_angle,
        "back_angle": back_angle,
        "neck_angle": neck_angle,
        "kp_hip":     hip,
        "kp_knee":    knee,
        "kp_shoulder":sho,
    }
