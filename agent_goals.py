# agent_goals.py 

# AGENTE INTELIGENTE - NUCLEO DEL SISTEMA

# La capa deliberativa del agente. El GoalSelector analiza el modelo del usuario y
# decide en que error concentrarse en este momento - en lugar de reportar todos
# los problemas a la vez- Si la fatiga supera el 70%, el objetivo cambio a descanso
# Esto es lo que convierte al sistema en un agente goal-directed y no un simple 
# detector de errores

from enum import Enum


class CoachingGoal(Enum):
    ESTABLISH_DEPTH  = "squat_depth"
    FIX_KNEE_VALGUS  = "knee_valgus"
    CORRECT_LEAN     = "trunk_lean"
    FIX_BACK         = "back_rounding"
    FIX_NECK         = "neck_alignment"
    MANAGE_FATIGUE   = "manage_fatigue"
    MAINTAIN_FORM    = "maintain_form"


GOAL_MESSAGES = {
    CoachingGoal.ESTABLISH_DEPTH: "Focus: reach parallel depth this set",
    CoachingGoal.FIX_KNEE_VALGUS: "Focus: push knees out over toes",
    CoachingGoal.CORRECT_LEAN:    "Focus: chest up, keep torso upright",
    CoachingGoal.FIX_BACK:        "Focus: neutral spine — hinge at the hips",
    CoachingGoal.FIX_NECK:        "Focus: neutral neck, gaze forward",
    CoachingGoal.MANAGE_FATIGUE:  "Consider resting — form is breaking down",
    CoachingGoal.MAINTAIN_FORM:   "Form is good — stay consistent",
}

ERROR_TO_GOAL = {
    "squat_depth":  CoachingGoal.ESTABLISH_DEPTH,
    "knee_valgus":  CoachingGoal.FIX_KNEE_VALGUS,
    "trunk_lean":   CoachingGoal.CORRECT_LEAN,
    "back_rounding":CoachingGoal.FIX_BACK,
    "neck_alignment":CoachingGoal.FIX_NECK,
}


class GoalSelector:
    def select(self, user_model) -> CoachingGoal:
        if user_model.fatigue_score > 0.70:
            return CoachingGoal.MANAGE_FATIGUE
        dominant = user_model.dominant_error()
        return ERROR_TO_GOAL.get(dominant, CoachingGoal.MAINTAIN_FORM)