import os
from typing import Optional
from vosk import Model

# Simple module-level cache for a single Vosk Model instance
_cached_model: Optional[Model] = None


def get_vosk_model(model_path: str = "model") -> Model:
    """Return a cached Vosk Model, loading it once per process.

    This prevents creating multiple heavy Model instances which can cause
    out-of-memory issues on low-RAM systems.

    Auto-detects the correct model path if 'model' is provided.
    """
    global _cached_model
    if _cached_model is None:
        # Auto-detect model path if default 'model' is used
        if model_path == "model" or not os.path.exists(model_path):
            detected_path = _detect_vosk_model_path()
            if detected_path:
                model_path = detected_path
                print(f"[VoskManager] Auto-detected model path: {model_path}")
            else:
                raise FileNotFoundError(f"No valid Vosk model found in '{model_path}' directory")

        _cached_model = Model(model_path)
        print(f"[VoskManager] Model loaded successfully from: {model_path}")
    return _cached_model


def _detect_vosk_model_path(base_path: str = "model") -> Optional[str]:
    """Auto-detect the Vosk model path by looking for valid model directories."""
    if not os.path.exists(base_path):
        return None

    # List of known Vosk model prefixes
    model_prefixes = ["vosk-model", "model"]

    # Check for direct model files (final.mdl)
    for root, dirs, files in os.walk(base_path):
        if "final.mdl" in files:
            return root

    # Check for subdirectories with model prefixes
    for item in os.listdir(base_path):
        item_path = os.path.join(base_path, item)
        if os.path.isdir(item_path) and any(item.startswith(prefix) for prefix in model_prefixes):
            # Verify it has the model file
            if os.path.exists(os.path.join(item_path, "am", "final.mdl")):
                return item_path

    return None
