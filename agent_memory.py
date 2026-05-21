# agent_memory.py 

# AGENTE INTELIGENTE - NUCLEO DEL SISTEMA

# Persistencia entre sesiones. Guarda un archivo JSON por usuario en la
# carpeta memory/ con el historial de sesiones, tasas de error
# por regla y score de fatiga. Calcula tendencias de mejora o deterioro 
# para mostrar progreso. Es lo que convierte al agente en un sistema 
# learning-capable - recuerda tu historial en la proxima sesion

import json
import os
from datetime import datetime
from config import MEMORY_DIR


class AgentMemory:
    def __init__(self, user_id: str = "default"):
        os.makedirs(MEMORY_DIR, exist_ok=True)
        self.filepath = os.path.join(MEMORY_DIR, f"{user_id}.json")
        self.data = self._load()

    def _load(self) -> dict:
        if os.path.exists(self.filepath):
            with open(self.filepath) as f:
                return json.load(f)
        return {"user_id": "", "sessions": []}

    def save_session(self, user_model):
        session = {
            "date":       datetime.now().isoformat(),
            "exercise":   user_model.current_exercise,
            "reps":       user_model.reps_completed,
            "fatigue":    round(user_model.fatigue_score, 3),
            "error_rates": {
                rule: round(user_model.error_rate(rule), 3)
                for rule in user_model.error_history
            },
        }
        self.data["sessions"].append(session)
        with open(self.filepath, "w") as f:
            json.dump(self.data, f, indent=2)

    def trend(self, rule: str, last_n: int = 5) -> float:
        """
        Improvement trend for a rule over last N sessions.
        Positive value = improving (error rate decreased).
        """
        sessions = self.data["sessions"][-last_n:]
        rates    = [s["error_rates"].get(rule, 0.0) for s in sessions]
        if len(rates) < 2:
            return 0.0
        return rates[0] - rates[-1]

    def total_sessions(self) -> int:
        return len(self.data["sessions"])

    def last_session_summary(self) -> dict | None:
        if not self.data["sessions"]:
            return None
        return self.data["sessions"][-1]