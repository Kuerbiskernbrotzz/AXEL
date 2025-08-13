# transcriber_util.py

from faster_whisper import WhisperModel
from logger.logger import log
# Konfiguration – kann später aus einer Config-Datei geladen werden
MODEL_SIZE = "small"
BEAM_SIZE = 5
DEVICE = "cuda"  # Alternativ "cpu"
COMPUTE_TYPE = "float32"  # z.B. "int8", "float16", "float32"
CONDITION_ON_PREVIOUS_TEXT = False
log.info("stt initialized.")

def transcribe_audio(path: str) -> str:
    """
    Transcribes a audio file and gives the transcribed text back..

    Args:
        path (str): Pfad zur WAV-Datei.

    Returns:
        str: Transkribierter Text.
    """
    # Initialisiere das Modell; beachte, dass das erste Argument model_size_or_path erwartet.
    model = WhisperModel(MODEL_SIZE, device=DEVICE, compute_type=COMPUTE_TYPE)

    # Führe die Transkription durch
    segments, _ = model.transcribe(
        path,
        beam_size=BEAM_SIZE,
        condition_on_previous_text=CONDITION_ON_PREVIOUS_TEXT
    )

    # Alle Segmente zu einem Text zusammenfügen
    transcript = "".join(segment.text for segment in segments)
    return transcript
