# rules/__init__.py

# CAPA DE RAZONAMIENTO - MOTOR DE REGLAS BIOMECANICAS

# Expmone la API publica del paquete rules/. Permite importar con 
# from rules import analyze_squat, Severity desde cualquier parte
# del proyecto sin conocer la estructua interna de carpetas

from .base_rules import Finding, AnalysisResult, Severity
from .squat_rules import analyze_squat
from .deadlift_rules import analyze_deadlift

__all__ = [
    "Finding", "AnalysisResult", "Severity",
    "analyze_squat", "analyze_deadlift",
]