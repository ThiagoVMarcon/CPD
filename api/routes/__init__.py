from .patients import patients_bp
from .admissions import admissions_bp
from .questions import questions_bp
# from .media import media_bp  # Não usado no momento

__all__ = [
    'patients_bp',
    'admissions_bp',
    'questions_bp',
    # 'media_bp'  # Não usado no momento
] 