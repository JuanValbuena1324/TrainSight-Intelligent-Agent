# agent.py 

# AGENTE INTELIGENTE - NUCLEO DEL SISTEMA

# El nucleo del agente inteligente. Orquesta el ciclo perceive-and-act: actualiza
# el modelo del mundo, selecciona el objetivo de coaching, aplica debouncing a los 
# hallazgos (solo repota errores sostenidos por N frames), filtra los Finding segun
# el objetivo actual y calcula tendencias de memoria. Es el unico archivo que une 
# las capas en cada frame

from agent_model import UserModel
from agent_goals import GoalSelector, GOAL_MESSAGES, ERROR_TO_GOAL
from agent_memory import AgentMemory
from rules.base_rules import Severity


class ExerciseCorrectionAgent:
    """
    A model-based, goal-directed intelligent agent for exercise correction.

    Perception  → angles.py / pose.py (external)
    World model → UserModel  (internal state)
    Goal select → GoalSelector (deliberative layer)
    Action      → returns structured feedback dict for overlay.py
    Memory      → AgentMemory (cross-session learning)
    """

    def __init__(self, user_id: str = "default", exercise: str = "squat"):
        self.user_model   = UserModel(current_exercise=exercise)
        self.goal_sel     = GoalSelector()
        self.memory       = AgentMemory(user_id)
        self.current_goal = None
        self._debounce: dict[str, int] = {}
        self.DEBOUNCE_FRAMES = 8

    def perceive_and_act(self, analysis_result, rep_completed: bool) -> dict:
        """
        Core agent loop — called every frame.
        Updates world model, selects goal, returns feedback action.
        """
        # 1. Update internal world model with new observation
        self.user_model.update(analysis_result, rep_completed)

        # 2. Select the current coaching goal (deliberation)
        self.current_goal = self.goal_sel.select(self.user_model)

        # 3. Debounce findings — only surface errors sustained for N frames
        stable_findings = []
        for finding in analysis_result.findings:
            key = finding.rule
            if finding.severity != Severity.OK:
                self._debounce[key] = self._debounce.get(key, 0) + 1
            else:
                self._debounce[key] = 0

            if (finding.severity == Severity.OK or
                    self._debounce.get(key, 0) >= self.DEBOUNCE_FRAMES):
                stable_findings.append(finding)

        # 4. Filter to findings relevant to the current goal
        goal_rule = self.current_goal.value
        goal_findings = [f for f in stable_findings if goal_rule in f.rule]
        display_findings = goal_findings if goal_findings else stable_findings[:2]

        # 5. Compute trends from memory for display
        trends = {
            rule: self.memory.trend(rule)
            for rule in self.user_model.error_history
        }

        return {
            "goal":         self.current_goal,
            "goal_message": GOAL_MESSAGES[self.current_goal],
            "findings":     display_findings,
            "all_findings": stable_findings,
            "reps":         self.user_model.reps_completed,
            "fatigue":      self.user_model.fatigue_score,
            "trends":       trends,
            "severity":     analysis_result.worst_severity,
        }

    def end_session(self):
        """Call when the user quits — persists the session to disk."""
        self.memory.save_session(self.user_model)