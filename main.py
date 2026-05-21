# main.py 

# PUNTO DE ENTRADA

# El bucle principal del programa. Instancia todas las capas y ejecuta el ciclo 
# continuo: leer frame -> estimar pose -> calcular angulos -> suavizar -> detectar 
# fase -> analizar reglas -> decision del agente -> dibujar overlay. Al salir (tecla q)
# lla,a a agent.end_session() para guardar la sesion en memoria. Cambiar entre squar
# y deadlift se hace aqui con la variable EXERCISE

# main.py
import cv2
from capture       import VideoCapture
from pose          import PoseEstimator
from angles        import compute_squat_angles, compute_deadlift_angles
from smoother      import AngleSmoother
from state_tracker import SquatTracker, SquatPhase
from rules         import analyze_squat, analyze_deadlift, Severity
from agent         import ExerciseCorrectionAgent
from overlay       import (draw_angle_label, draw_joint_highlight,
                           draw_feedback_panel)

EXERCISE = "squat"      # change to "deadlift" if needed
USER_ID  = "athlete1"   # used for memory file in memory/


def main():
    estimator = PoseEstimator()
    smoother  = AngleSmoother()
    tracker   = SquatTracker()
    agent     = ExerciseCorrectionAgent(user_id=USER_ID, exercise=EXERCISE)

    try:
        with VideoCapture() as cam:
            while True:
                ok, frame = cam.read()
                if not ok:
                    break

                # ── Perception ─────────────────────────────────────
                landmarks, pose_lm = estimator.process(frame)
                estimator.draw_skeleton(frame, pose_lm)

                if landmarks is None:
                    cv2.putText(
                        frame,
                        "No pose detected — adjust position",
                        (30, 50),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7, (100, 100, 255), 2
                    )
                    cv2.imshow("Exercise Agent", frame)
                    if cv2.waitKey(1) & 0xFF == ord("q"):
                        break
                    continue

                # ── Angle extraction + smoothing ───────────────────
                raw_angles = (
                    compute_squat_angles(landmarks)
                    if EXERCISE == "squat"
                    else compute_deadlift_angles(landmarks)
                )

                if raw_angles is None:
                    cv2.imshow("Exercise Agent", frame)
                    if cv2.waitKey(1) & 0xFF == ord("q"):
                        break
                    continue

                angles = smoother.smooth(raw_angles)

                # ── State tracking + rep counting ──────────────────
                prev_reps = tracker.rep_count
                phase     = tracker.update(angles.get("avg_knee", 180))

                # fires True only on the exact frame a rep is counted
                rep_completed = tracker.rep_count > prev_reps

                # ── Rule-based reasoning ───────────────────────────
                result = (
                    analyze_squat(angles, phase.value)
                    if EXERCISE == "squat"
                    else analyze_deadlift(angles, phase.value)
                )

                # ── Agent deliberation ─────────────────────────────
                action = agent.perceive_and_act(result, rep_completed)

                # ── Pass all values to HUD panels ──────────────────
                action["reps"]         = tracker.rep_count
                action["hud_phase"]    = phase.value
                action["hud_knee"]     = float(angles.get("avg_knee",           0.0))
                action["hud_trunk"]    = float(angles.get("trunk_lean",          0.0))
                action["hud_foot"]     = float(angles.get("foot_shoulder_ratio", 0.0))
                action["all_findings"] = result.findings

                # ── Visual overlays ────────────────────────────────
                if EXERCISE == "squat":

                    # Depth finding drives knee label color
                    depth_finding = next(
                        (f for f in result.findings if f.rule == "squat_depth"),
                        None
                    )
                    depth_severity = (
                        depth_finding.severity if depth_finding else Severity.OK
                    )

                    # Trunk finding drives trunk label color
                    trunk_finding = next(
                        (f for f in result.findings if f.rule == "trunk_lean"),
                        None
                    )
                    trunk_severity = (
                        trunk_finding.severity if trunk_finding else Severity.OK
                    )

                    # Single avg knee label
                    draw_angle_label(
                        frame,
                        angles["kp_left_knee"],
                        angles["avg_knee"],
                        "Knee avg",
                        depth_severity
                    )

                    # Trunk lean label
                    draw_angle_label(
                        frame,
                        angles["kp_mid_hip"],
                        angles["trunk_lean"],
                        "trunk",
                        trunk_severity
                    )

                    # ── Foot position overlay ──────────────────────
                    foot_finding = next(
                        (f for f in result.findings if f.rule == "foot_position"),
                        None
                    )
                    foot_severity = (
                        foot_finding.severity if foot_finding else Severity.OK
                    )

                    # Linea entre tobillos
                    if "kp_left_ankle" in angles and "kp_right_ankle" in angles:
                        cv2.line(
                            frame,
                            (int(angles["kp_left_ankle"][0]),
                             int(angles["kp_left_ankle"][1])),
                            (int(angles["kp_right_ankle"][0]),
                             int(angles["kp_right_ankle"][1])),
                            (60, 200, 90) if foot_severity == Severity.OK
                            else (50, 50, 220),
                            2, cv2.LINE_AA
                        )

                    # Linea entre hombros — referencia amarilla
                    if "kp_left_shoulder" in angles and "kp_right_shoulder" in angles:
                        cv2.line(
                            frame,
                            (int(angles["kp_left_shoulder"][0]),
                             int(angles["kp_left_shoulder"][1])),
                            (int(angles["kp_right_shoulder"][0]),
                             int(angles["kp_right_shoulder"][1])),
                            (36, 200, 255),
                            2, cv2.LINE_AA
                        )

                    # Label ratio pie/hombro
                    if "kp_left_ankle" in angles and "foot_shoulder_ratio" in angles:
                        draw_angle_label(
                            frame,
                            angles["kp_left_ankle"],
                            angles["foot_shoulder_ratio"],
                            "pie/hombro",
                            foot_severity
                        )

                    # Highlight tobillos si hay error
                    if foot_finding and foot_finding.severity == Severity.ERROR:
                        if "kp_left_ankle" in angles:
                            draw_joint_highlight(
                                frame,
                                angles["kp_left_ankle"],
                                foot_finding.severity
                            )
                        if "kp_right_ankle" in angles:
                            draw_joint_highlight(
                                frame,
                                angles["kp_right_ankle"],
                                foot_finding.severity
                            )

                    # Highlight joints with errors
                    for finding in action["findings"]:
                        if finding.severity == Severity.ERROR:
                            if "knee_valgus" in finding.rule:
                                draw_joint_highlight(
                                    frame,
                                    angles["kp_left_knee"],
                                    finding.severity
                                )
                                draw_joint_highlight(
                                    frame,
                                    angles["kp_right_knee"],
                                    finding.severity
                                )
                            elif "trunk" in finding.rule:
                                draw_joint_highlight(
                                    frame,
                                    angles["kp_mid_hip"],
                                    finding.severity
                                )
                            elif "depth" in finding.rule:
                                draw_joint_highlight(
                                    frame,
                                    angles["kp_left_knee"],
                                    finding.severity
                                )
                                draw_joint_highlight(
                                    frame,
                                    angles["kp_right_knee"],
                                    finding.severity
                                )

                elif EXERCISE == "deadlift":

                    draw_angle_label(
                        frame,
                        angles["kp_knee"],
                        angles["knee_angle"],
                        "knee",
                        result.worst_severity
                    )
                    draw_angle_label(
                        frame,
                        angles["kp_hip"],
                        angles["back_angle"],
                        "back",
                        Severity.ERROR if angles["back_angle"] > 45
                        else Severity.OK
                    )

                    for finding in action["findings"]:
                        if finding.severity == Severity.ERROR:
                            if "back" in finding.rule:
                                draw_joint_highlight(
                                    frame,
                                    angles["kp_hip"],
                                    finding.severity
                                )
                            elif "knee" in finding.rule:
                                draw_joint_highlight(
                                    frame,
                                    angles["kp_knee"],
                                    finding.severity
                                )

                # ── HUD panel ──────────────────────────────────────
                print(f"hud_knee={action.get('hud_knee')}  hud_trunk={action.get('hud_trunk')}  hud_foot={action.get('hud_foot')}  hud_phase={action.get('hud_phase')}")
                draw_feedback_panel(frame, action)

                cv2.imshow("Exercise Agent", frame)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break

    finally:
        agent.end_session()
        estimator.close()
        cv2.destroyAllWindows()
        print(f"Session saved. Total sessions: {agent.memory.total_sessions()}")


if __name__ == "__main__":
    main()

    
