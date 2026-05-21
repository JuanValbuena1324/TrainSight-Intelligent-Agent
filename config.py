# config.py

# CAPA DE CONFIGURACION

# Archivo central de parametros. Contiene todos los umbrales biomecanicos (angulos,
# del squat, deadlift), ajuestes de MediaPipe, tamaño de ventan del smoother y rutas
# de archivos. Si necesitas ajustar un umbral, solo cambias aqui - sin tocar el resto 
# del codigo

VIDEO_SOURCE = 0
DISPLAY_WIDTH  = 1280
DISPLAY_HEIGHT = 720

MIN_DETECTION_CONFIDENCE = 0.7
MIN_TRACKING_CONFIDENCE  = 0.5
LANDMARK_VISIBILITY_THRESHOLD = 0.5

ANGLE_SMOOTHING_WINDOW = 6     # frames for rolling average
FEEDBACK_DEBOUNCE_FRAMES = 8     # frames before an error is reported

SQUAT = {
    "knee_angle_depth_perfect_min": 85,
    "knee_angle_depth_perfect_max": 95,
    "knee_angle_too_deep":          80,
    "knee_angle_too_shallow":      100,
    "trunk_lean_max":               50,
    "knee_valgus_ratio_min":        0.80,
    "foot_shoulder_ratio_min":      0.85,   # ← pies muy juntos
    "foot_shoulder_ratio_max":      1.35,   # ← pies muy abiertos
}

DEADLIFT = {
    "back_angle_max":   45,
    "knee_angle_min":   80,
    "neck_angle_max":   30,
}

MEMORY_DIR = "memory/"