main.py llama a capture.py para obtener un frame, 
lo pasa a pose.py que extrae 33 landmarks con MediaPipe, 
luego angles.py convierte esos landmarks en ángulos articulares, 
smoother.py elimina el jitter, state_tracker.py detecta la fase del movimiento, 
rules/ aplica las reglas biomecánicas y produce findings, 
agent.py los procesa con su modelo interno y selecciona el objetivo de coaching apoyándose en agent_model.py, 
agent_goals.py y agent_memory.py, y finalmente overlay.py dibuja todo sobre el frame con OpenCV.