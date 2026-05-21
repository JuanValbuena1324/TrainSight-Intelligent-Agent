
# pose.py

# CAPA DE PERCEPCION . CAPA SENSORIAL DEL AGENTE

# Envuelve MediaPipe PoseLandmarker (nueva Tacks API), descarga el modelo
# automaticamente en el primer uso. Procesa cada frame y retorna un diccionario
# de landmarks con posicion en pixeles, profundidad Z y visibilidad. Tambien
# dibuja el esqueleto sobre el frame. Contiene la clase LM con los indices
# de cada articulacion

import os
import urllib.request
import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision as mp_vision
from mediapipe.tasks.python.vision import PoseLandmarkerOptions

from config import MIN_DETECTION_CONFIDENCE, MIN_TRACKING_CONFIDENCE

MODEL_PATH = "pose_landmarker_full.task"
MODEL_URL  = (
    "https://storage.googleapis.com/mediapipe-models/"
    "pose_landmarker/pose_landmarker_full/float16/latest/"
    "pose_landmarker_full.task"
)

def _ensure_model():
    if not os.path.exists(MODEL_PATH):
        print("Downloading pose model (~10 MB) ...")
        urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)
        print("Download complete.")


class LM:
    """Landmark index constants — same numbering as the old MediaPipe enum."""
    NOSE            = 0
    LEFT_EAR        = 7
    RIGHT_EAR       = 8
    LEFT_SHOULDER   = 11
    RIGHT_SHOULDER  = 12
    LEFT_HIP        = 23
    RIGHT_HIP       = 24
    LEFT_KNEE       = 25
    RIGHT_KNEE      = 26
    LEFT_ANKLE      = 27
    RIGHT_ANKLE     = 28


# Skeleton connections for drawing (index pairs)
POSE_CONNECTIONS = [
    (11,12),(11,13),(13,15),(12,14),(14,16),  # arms
    (11,23),(12,24),(23,24),                   # torso
    (23,25),(25,27),(24,26),(26,28),           # legs
    (0,7),(0,8),                               # head
]


class PoseEstimator:
    def __init__(self):
        _ensure_model()
        base_opts = mp_python.BaseOptions(model_asset_path=MODEL_PATH)
        opts = PoseLandmarkerOptions(
            base_options=base_opts,
            running_mode=mp_vision.RunningMode.VIDEO,
            num_poses=1,
            min_pose_detection_confidence=MIN_DETECTION_CONFIDENCE,
            min_pose_presence_confidence=MIN_DETECTION_CONFIDENCE,
            min_tracking_confidence=MIN_TRACKING_CONFIDENCE,
            output_segmentation_masks=False,
        )
        self.landmarker  = mp_vision.PoseLandmarker.create_from_options(opts)
        self._frame_ts   = 0   # monotonic ms timestamp required by VIDEO mode

    def process(self, frame):
        """
        Returns (landmarks_dict | None, raw_result | None).
        landmarks_dict: {int_index: np.array([px_x, px_y, z, visibility])}
        """
        self._frame_ts += 33   # increment ~30 fps

        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB),
        )
        result = self.landmarker.detect_for_video(mp_image, self._frame_ts)

        if not result.pose_landmarks:
            return None, None

        h, w   = frame.shape[:2]
        lm_raw = result.pose_landmarks[0]
        lm     = {}
        for idx, point in enumerate(lm_raw):
            lm[idx] = np.array([
                point.x * w,
                point.y * h,
                point.z,
                getattr(point, "visibility", 1.0),
            ])
        return lm, result

    def draw_skeleton(self, frame, result):
        if result is None or not result.pose_landmarks:
            return frame

        h, w   = frame.shape[:2]
        lm_raw = result.pose_landmarks[0]

        for start, end in POSE_CONNECTIONS:
            if start >= len(lm_raw) or end >= len(lm_raw):
                continue
            s, e = lm_raw[start], lm_raw[end]
            if getattr(s, "visibility", 1.0) < 0.5:
                continue
            if getattr(e, "visibility", 1.0) < 0.5:
                continue
            cv2.line(frame,
                     (int(s.x * w), int(s.y * h)),
                     (int(e.x * w), int(e.y * h)),
                     (0, 200, 100), 2, cv2.LINE_AA)

        for point in lm_raw:
            if getattr(point, "visibility", 1.0) < 0.5:
                continue
            cv2.circle(frame,
                       (int(point.x * w), int(point.y * h)),
                       4, (255, 255, 255), -1)

        return frame

    def close(self):
        self.landmarker.close()