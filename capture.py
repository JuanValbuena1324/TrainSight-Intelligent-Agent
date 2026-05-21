# capture.py 

# CAPA DE PERCEPCION - CAPA SENSORIAL DEL AGENTE

# Abstrae la camara o archivo de video usando OpenCV. El resto del sistema
# no sabe si la fuente es una webcam, un video MP4 o una camara IP - solo
# pide frames. Soporta uso como context manager (with VideoCapture()) para
# liberar la camar correctamente al salir

import cv2
from config import VIDEO_SOURCE, DISPLAY_WIDTH, DISPLAY_HEIGHT


class VideoCapture:
    def __init__(self, source=VIDEO_SOURCE):
        self.cap = cv2.VideoCapture(source)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH,  DISPLAY_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, DISPLAY_HEIGHT)
        if not self.cap.isOpened():
            raise RuntimeError(f"Cannot open video source: {source}")

    def read(self):
        ret, frame = self.cap.read()
        return (False, None) if not ret else (True, frame)

    def release(self):
        self.cap.release()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.release()