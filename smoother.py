# smoother.py

# CAPA DE PERCEPCION - CAPA SENSORIAL DEL AGENTE

# Aplica un promedio movil (rolling average) sobre los angulos calculados frame a 
# frame. Sin este filtro, los valoes de MediaPipe tiemblan visiblemente y el motor
# de reglas dispararia erroes falsos en cada frame. La ventana de suavizado es 
# configurable en config.py

from collections import deque
import numpy as np


class AngleSmoother:
    def __init__(self, window: int = 6):
        self.window   = window
        self._buffers: dict[str, deque] = {}

    def smooth(self, angles: dict) -> dict:
        smoothed = {}
        for key, val in angles.items():
            if not isinstance(val, (int, float)):
                smoothed[key] = val          # pass non-numeric values through
                continue
            if key not in self._buffers:
                self._buffers[key] = deque(maxlen=self.window)
            self._buffers[key].append(val)
            smoothed[key] = float(np.mean(self._buffers[key]))
        return smoothed

    def reset(self):
        self._buffers.clear()