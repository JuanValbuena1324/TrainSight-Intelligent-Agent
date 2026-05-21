# agent_model.py 

# AGENTE INTELIGENTE - NUCLEO DEL SISTEMA

# El modelo interno del mundo que mantiene el agente. Registra el historial de
# errores por regla (ventana deslizante de las ultimas 10 reps), cuenta las reps
# completados y estima un scroe de fatiga basado en la degradacion de la tecnica
# Es la memoria de trabajo de sesion - lo que hace al agente model-based en lugar
# de reactibo puro 

from dataclasses import dataclass, field
from datetime import datetime
import uuid


@dataclass
class UserModel:
    session_id:   str = field(default_factory=lambda: str(uuid.uuid4()))
    start_time:   datetime = field(default_factory=datetime.now)
    current_exercise: str = "squat"
    reps_completed:   int = 0
    fatigue_score:    float = 0.0   # 0–1, grows as form degrades over reps

    error_history: dict = field(default_factory=lambda: {
        "squat_depth":  [],
        "trunk_lean":   [],
        "knee_valgus":  [],
        "asymmetry":    [],
        "back_rounding":[],
        "deadlift_knee":[],
        "neck_alignment":[],
    })

    def update(self, analysis_result, rep_completed: bool):
        if rep_completed:
            self.reps_completed += 1
            for finding in analysis_result.findings:
                hist = self.error_history.get(finding.rule)
                if hist is None:
                    continue
                hist.append(1 if finding.severity.value != "ok" else 0)
                if len(hist) > 10:
                    hist.pop(0)
            self._update_fatigue()

    def _update_fatigue(self):
        if self.reps_completed < 3:
            return
        recent_errors = [
            sum(h[-3:]) / max(len(h[-3:]), 1)
            for h in self.error_history.values()
            if h
        ]
        if recent_errors:
            self.fatigue_score = min(1.0, sum(recent_errors) / len(recent_errors))

    def error_rate(self, rule: str) -> float:
        hist = self.error_history.get(rule, [])
        return sum(hist) / len(hist) if hist else 0.0

    def dominant_error(self) -> str | None:
        rates = {
            r: self.error_rate(r)
            for r in self.error_history
            if self.error_history[r]
        }
        if not rates:
            return None
        worst = max(rates, key=rates.get)
        return worst if rates[worst] > 0.35 else None