from typing import Optional
from vosk import Model

# Simple module-level cache for a single Vosk Model instance
_cached_model: Optional[Model] = None


def get_vosk_model(model_path: str = "model") -> Model:
    """Return a cached Vosk Model, loading it once per process.

    This prevents creating multiple heavy Model instances which can cause
    out-of-memory issues on low-RAM systems.
    """
    global _cached_model
    if _cached_model is None:
        _cached_model = Model(model_path)
    return _cached_model
