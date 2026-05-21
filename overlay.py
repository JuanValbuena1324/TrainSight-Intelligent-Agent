# overlay.py 

# SALIDA VISUAL 

# Todo el codigo de dibujo con OpenCV: rtiquetas de angulos junto a las 
# articulaciones, circulos de resaltado en joints con error, y el panel
# HUD semi-transparente con objetivo activo, repeticiones, fatiga, cues
# de coaching y tendencias de sesion. Separado del agente para que el
# feedback visual sea intercambiable sin tocar la logica

# overlay.py
import cv2
import numpy as np
from rules.base_rules import Severity

C = {
    "green":      (74,  222, 128),
    "amber":      (36,  191, 251),
    "red":        (113, 113, 248),
    "white":      (255, 255, 255),
    "panel_bg":   (10,   10,  10),
    "muted":      (140, 140, 140),
    "dim":        (70,   70,  70),
    "divider":    (45,   45,  45),
    "goal_bg":    (15,   45,  15),
    "goal_bord":  (40,  100,  40),
    "badge_bg":   (22,   22,  22),
}

SEV_COLOR = {
    Severity.OK:      C["green"],
    Severity.WARNING: C["amber"],
    Severity.ERROR:   C["red"],
}


# ── Primitives ───────────────────────────────────────────────────────────────

def _txt(frame, text, x, y, color, scale=0.5, thickness=1):
    text = text.encode("ascii", "replace").decode("ascii").replace("?", "")
    cv2.putText(frame, text, (x, y),
                cv2.FONT_HERSHEY_SIMPLEX, scale, color, thickness, cv2.LINE_AA)


def _panel(frame, x1, y1, x2, y2, alpha=0.85):
    overlay = frame.copy()
    cv2.rectangle(overlay, (x1, y1), (x2, y2), C["panel_bg"], -1)
    cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)


def _hline(frame, x1, x2, y, color=None):
    cv2.line(frame, (x1, y), (x2, y),
             color or C["divider"], 1, cv2.LINE_AA)


def _dot(frame, x, y, color, r=5):
    cv2.circle(frame, (x, y), r, color, -1, cv2.LINE_AA)


def _tw(text, scale, thickness=1):
    text = text.encode("ascii", "replace").decode("ascii")
    return cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX,
                           scale, thickness)[0][0]


# ── Joint overlays ───────────────────────────────────────────────────────────

def draw_angle_label(frame, point: np.ndarray, angle: float,
                     label: str, severity: Severity = Severity.OK):
    x     = int(point[0]) + 12
    y     = int(point[1]) - 12
    color = SEV_COLOR[severity]
    text  = f"{label}: {angle:.0f}"
    w_txt = _tw(text, 0.52)
    th    = 16
    cv2.rectangle(frame, (x - 5, y - th - 4), (x + w_txt + 6, y + 6),
                  (0, 0, 0), -1)
    cv2.rectangle(frame, (x - 5, y - th - 4), (x + w_txt + 6, y + 6),
                  color, 1)
    _txt(frame, text, x, y, color, scale=0.52, thickness=1)


def draw_joint_highlight(frame, point: np.ndarray, severity: Severity,
                         radius: int = 16):
    if severity == Severity.OK:
        return
    x, y  = int(point[0]), int(point[1])
    color = SEV_COLOR[severity]
    cv2.circle(frame, (x, y), radius,     color, 2, cv2.LINE_AA)
    cv2.circle(frame, (x, y), radius - 5, color, 1, cv2.LINE_AA)


# ── Main HUD ─────────────────────────────────────────────────────────────────

def draw_feedback_panel(frame, action: dict):
    h, w = frame.shape[:2]
    _draw_left_panel(frame, action, h, w)
    _draw_right_panel(frame, action, h, w)


# ── LEFT PANEL ───────────────────────────────────────────────────────────────

def _draw_left_panel(frame, action: dict, h: int, w: int):
    PW = 280
    _panel(frame, 0, 0, PW, h)
    cv2.line(frame, (PW, 0), (PW, h), C["divider"], 1)

    y = 30
    M = 16

    # ── Logo ────────────────────────────────────────────────────────
    _txt(frame, "Train", M, y, C["white"],  scale=0.75, thickness=2)
    offset = _tw("Train", 0.75, 2) + M
    _txt(frame, "Sight", offset, y, C["green"], scale=0.75, thickness=2)
    y += 20
    _hline(frame, M, PW - M, y)
    y += 16

    # ── Exercise / Phase ─────────────────────────────────────────────
    _txt(frame, "EJERCICIO", M, y, C["dim"], scale=0.36)
    _txt(frame, "FASE", M + 130, y, C["dim"], scale=0.36)
    y += 16

    _txt(frame, "Squat", M, y, C["white"], scale=0.58, thickness=1)

    phase     = str(action.get("hud_phase", "standing"))
    phase_map = {
        "standing":   ("STANDING",  C["white"]),
        "descending": ("BAJANDO",   C["amber"]),
        "bottom":     ("ABAJO",     C["green"]),
        "ascending":  ("SUBIENDO",  C["green"]),
    }
    phase_txt, phase_col = phase_map.get(phase, (phase.upper(), C["white"]))
    _txt(frame, phase_txt, M + 130, y, phase_col, scale=0.52, thickness=1)
    y += 22
    _hline(frame, M, PW - M, y)
    y += 14

    # ── Goal box ─────────────────────────────────────────────────────
    goal_msg = action.get("goal_message", "Form is good - stay consistent")
    goal_msg = goal_msg.encode("ascii", "replace").decode("ascii").replace("?", "")

    box_h   = 58
    overlay = frame.copy()
    cv2.rectangle(overlay, (M, y), (PW - M, y + box_h), C["goal_bg"], -1)
    cv2.addWeighted(overlay, 0.92, frame, 0.08, 0, frame)
    cv2.rectangle(frame, (M, y), (PW - M, y + box_h), C["goal_bord"], 1)

    _txt(frame, "OBJETIVO", M + 8, y + 14, C["muted"], scale=0.34)

    words = goal_msg.split()
    lines = [""]
    for word in words:
        test = (lines[-1] + " " + word).strip()
        if _tw(test, 0.46) < PW - M - 20:
            lines[-1] = test
        else:
            lines.append(word)
    for i, line in enumerate(lines[:2]):
        _txt(frame, line, M + 8, y + 30 + i * 18,
             C["green"], scale=0.46, thickness=1)
    y += box_h + 12

    # ── Findings ─────────────────────────────────────────────────────
    _txt(frame, "ANALISIS", M, y, C["dim"], scale=0.36)
    y += 14

    findings = action.get("all_findings", action.get("findings", []))
    for finding in findings:
        color = SEV_COLOR[finding.severity]
        cue   = finding.cue.encode("ascii", "replace").decode("ascii").replace("?", "")

        overlay = frame.copy()
        cv2.rectangle(overlay, (M, y), (PW - M, y + 28), (20, 20, 20), -1)
        cv2.addWeighted(overlay, 0.75, frame, 0.25, 0, frame)
        cv2.rectangle(frame, (M, y), (PW - M, y + 28), C["divider"], 1)

        _dot(frame, M + 12, y + 14, color, r=4)

        while _tw(cue, 0.42) > PW - M - 35:
            cue = cue[:-4] + "..."
        _txt(frame, cue, M + 24, y + 19, color, scale=0.42, thickness=1)
        y += 32

    y += 8
    _hline(frame, M, PW - M, y)
    y += 12

    # ── Trends ───────────────────────────────────────────────────────
    _txt(frame, "TENDENCIAS", M, y, C["dim"], scale=0.36)
    y += 16

    trends     = action.get("trends", {})
    rule_names = {
        "squat_depth":   "Profundidad",
        "trunk_lean":    "Tronco",
        "knee_valgus":   "Rodillas",
        "foot_position": "Pies",
        "asymmetry":     "Simetria",
    }

    for rule, label in rule_names.items():
        if rule not in trends:
            continue
        trend = trends[rule]
        arrow = "+" if trend > 0.05 else ("-" if trend < -0.05 else "=")
        color = (C["green"] if trend > 0.05
                 else C["red"] if trend < -0.05
                 else C["amber"])

        _txt(frame, label, M, y + 10, C["muted"], scale=0.38)

        bar_x1 = M + 90
        bar_x2 = PW - M - 22
        bar_y  = y + 6
        cv2.rectangle(frame, (bar_x1, bar_y),
                      (bar_x2, bar_y + 4), C["divider"], -1)
        fill = int((bar_x2 - bar_x1) * min(1.0, max(0.0, 0.5 + trend * 2)))
        if fill > 0:
            cv2.rectangle(frame, (bar_x1, bar_y),
                          (bar_x1 + fill, bar_y + 4), color, -1)

        _txt(frame, arrow, PW - M - 16, y + 12, color, scale=0.42)
        y += 20


# ── RIGHT PANEL ──────────────────────────────────────────────────────────────

def _draw_right_panel(frame, action: dict, h: int, w: int):
    PW = 150
    x0 = w - PW

    _panel(frame, x0, 0, w, h)
    cv2.line(frame, (x0, 0), (x0, h), C["divider"], 1)

    cx = x0 + PW // 2

    findings_map = {f.rule: f for f in action.get("all_findings", [])}

    knee_sev  = findings_map["squat_depth"].severity   if "squat_depth"   in findings_map else Severity.OK
    trunk_sev = findings_map["trunk_lean"].severity    if "trunk_lean"    in findings_map else Severity.OK
    foot_sev  = findings_map["foot_position"].severity if "foot_position" in findings_map else Severity.OK

    # ── Read values using hud_ keys ──────────────────────────────────
    knee_val  = float(action.get("hud_knee",  0.0))
    trunk_val = float(action.get("hud_trunk", 0.0))
    foot_val  = float(action.get("hud_foot",  0.0))

    def angle_badge(val, label, sev, y_pos):
        color = SEV_COLOR[sev]
        bx1, bx2 = x0 + 8, w - 8
        by1, by2 = y_pos, y_pos + 64

        overlay = frame.copy()
        cv2.rectangle(overlay, (bx1, by1), (bx2, by2), C["badge_bg"], -1)
        cv2.addWeighted(overlay, 0.92, frame, 0.08, 0, frame)
        cv2.rectangle(frame, (bx1, by1), (bx2, by2), color, 2)

        val_str = f"{val:.0f}" if val >= 1.0 else f"{val:.2f}"
        vtw     = _tw(val_str, 0.90, 2)
        _txt(frame, val_str, cx - vtw // 2, by1 + 40,
             color, scale=0.90, thickness=2)

        ltw = _tw(label, 0.32)
        _txt(frame, label, cx - ltw // 2, by1 + 56,
             C["muted"], scale=0.32)
        return by2 + 10

    y = 16
    y = angle_badge(knee_val,  "RODILLA AVG", knee_sev,  y)
    y = angle_badge(trunk_val, "TRONCO",      trunk_sev, y)
    y = angle_badge(foot_val,  "PIE/HOMBRO",  foot_sev,  y)

    # ── Phase pill ───────────────────────────────────────────────────
    phase     = str(action.get("hud_phase", "standing"))
    phase_map = {
        "standing":   ("STANDING",  C["white"]),
        "descending": ("BAJANDO",   C["amber"]),
        "bottom":     ("ABAJO",     C["green"]),
        "ascending":  ("SUBIENDO",  C["green"]),
    }
    phase_txt, phase_col = phase_map.get(phase, (phase.upper(), C["white"]))

    overlay = frame.copy()
    cv2.rectangle(overlay, (x0 + 8, y), (w - 8, y + 22), C["goal_bg"], -1)
    cv2.addWeighted(overlay, 0.9, frame, 0.1, 0, frame)
    cv2.rectangle(frame, (x0 + 8, y), (w - 8, y + 22), C["goal_bord"], 1)
    ptw = _tw(phase_txt, 0.38)
    _txt(frame, phase_txt, cx - ptw // 2, y + 15,
         phase_col, scale=0.38, thickness=1)
    y += 30

    # ── Rep counter ──────────────────────────────────────────────────
    reps    = str(action.get("reps", 0))
    rtw     = _tw(reps, 1.8, 3)
    _txt(frame, reps, cx - rtw // 2, y + 65,
         C["white"], scale=1.8, thickness=3)
    ltw = _tw("REPS", 0.36)
    _txt(frame, "REPS", cx - ltw // 2, y + 82,
         C["muted"], scale=0.36)
    y += 90

    # ── Fatigue bar ──────────────────────────────────────────────────
    fatigue   = float(action.get("fatigue", 0.0))
    fat_pct   = int(fatigue * 100)
    fat_color = (C["green"] if fat_pct < 40
                 else C["amber"] if fat_pct < 70
                 else C["red"])

    ftw = _tw("FATIGA", 0.34)
    _txt(frame, "FATIGA", cx - ftw // 2, y + 12,
         C["muted"], scale=0.34)
    y += 18

    bx1, bx2 = x0 + 10, w - 10
    cv2.rectangle(frame, (bx1, y), (bx2, y + 6), C["divider"], -1)
    fw = int((bx2 - bx1) * fatigue)
    if fw > 0:
        cv2.rectangle(frame, (bx1, y), (bx1 + fw, y + 6), fat_color, -1)
    y += 14

    pct_str = f"{fat_pct}%"
    ptw     = _tw(pct_str, 0.45)
    _txt(frame, pct_str, cx - ptw // 2, y + 14,
         fat_color, scale=0.45, thickness=1)
    