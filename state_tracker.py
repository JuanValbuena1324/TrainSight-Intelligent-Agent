# state_tracker.py 

# SEGUIMIENTO DE ESTADO

# Implementa una maquina de estados finitos (FSM) que detecta la 
# fase del squat: STANDING -> DESCENDING -> BOTTOM -> ASCENDING -> STANDING
# Cuenta repeticiones automaticamente al detectar el ciclo completo. Es
# lo que le da al agente conciencia temportal - sabe en que parte del 
# movimiento esta el usuario en cada momento. 

# state_tracker.py
from enum import Enum


class SquatPhase(Enum):
    STANDING   = "standing"
    DESCENDING = "descending"
    BOTTOM     = "bottom"
    ASCENDING  = "ascending"


class SquatTracker:
    """
    Based on real measured values:
      Standing:  avg_knee ≈ 172–178°
      Deepest:   avg_knee ≈ 52–56°

    Thresholds set with safe margins:
      STAND_THRESHOLD = 165  (well below 172, counts as standing)
      DEPTH_THRESHOLD = 100  (well above 52, counts as bottom)
    """

    STAND_THRESHOLD = 165
    DEPTH_THRESHOLD = 100

    def __init__(self):
        self.phase      = SquatPhase.STANDING
        self.rep_count  = 0

        # Three flags that must fire IN ORDER for a rep to count
        self._went_down   = False   # crossed below DEPTH_THRESHOLD
        self._came_up     = False   # crossed above STAND_THRESHOLD after bottom
        self._prev_angle  = 180.0

    def update(self, avg_knee_angle: float) -> SquatPhase:

        prev = self._prev_angle
        self._prev_angle = avg_knee_angle

        # ── Detect crossing events ──────────────────────────────────

        # Just crossed DOWN into bottom zone
        crossed_into_bottom = (prev >= self.DEPTH_THRESHOLD and
                               avg_knee_angle < self.DEPTH_THRESHOLD)

        # Just crossed UP into standing zone
        crossed_into_standing = (prev < self.STAND_THRESHOLD and
                                 avg_knee_angle >= self.STAND_THRESHOLD)

        # ── Update flags ────────────────────────────────────────────

        if crossed_into_bottom:
            self._went_down = True

        if crossed_into_standing and self._went_down:
            # Completed full cycle: was at bottom, now back to standing
            self.rep_count += 1
            self._went_down = False   # reset for next rep

        # ── Update phase for display ────────────────────────────────

        if avg_knee_angle >= self.STAND_THRESHOLD:
            self.phase = SquatPhase.STANDING
        elif avg_knee_angle < self.DEPTH_THRESHOLD:
            self.phase = SquatPhase.BOTTOM
        elif avg_knee_angle < prev:
            self.phase = SquatPhase.DESCENDING
        else:
            self.phase = SquatPhase.ASCENDING

        return self.phase

    def reset(self):
        self.phase        = SquatPhase.STANDING
        self.rep_count    = 0
        self._went_down   = False
        self._came_up     = False
        self._prev_angle  = 180.0