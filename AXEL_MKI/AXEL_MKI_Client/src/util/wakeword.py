import threading
import math
import struct
import wave
import pyaudio
import pvporcupine
from .config import *
from .utils import resource_path 

from PyQt6.QtCore import QMetaObject, Q_ARG, Qt
from .logger import log

log.info("wakeword detection initialized")


def start_wakeword_detection(MainWindow):
    """Führt die Wakeword Detection und Audioaufnahme aus."""
    def run_wakeword():
        def rms(frame):
            return math.sqrt(sum(sample * sample for sample in frame) / len(frame))

        porcupine = pvporcupine.create(
            access_key=ACCESS_KEY,
            keyword_paths=[resource_path('models/porcupine_windows.ppn')]
        )
        pa = pyaudio.PyAudio()
        audio_stream = pa.open(
            rate=porcupine.sample_rate,
            channels=1,
            format=pyaudio.paInt16,
            input=True,
            frames_per_buffer=porcupine.frame_length
        )
        log.info("Wakeword detection ready.")
        try:
            while True:
                pcm_bytes = audio_stream.read(porcupine.frame_length)
                pcm = struct.unpack_from("h" * porcupine.frame_length, pcm_bytes)
                result = porcupine.process(pcm)
                if result >= 0:
                    log.info("Wakeword detected!")
                    break
                if not MainWindow.recording_active:
                    log.info("Wakeword Detection canceled.")
                    return

            # Visualizer in Listening-Modus
            QMetaObject.invokeMethod(MainWindow.visualizer, "set_mode", Qt.ConnectionType.QueuedConnection, Q_ARG(str, "listening"))

            log.info("Recording started...")
            frames = []
            silence_threshold = 120
            silence_frame_count = 0
            required_silence_frames = int(2 * (porcupine.sample_rate / porcupine.frame_length))

            while True:
                pcm_bytes = audio_stream.read(porcupine.frame_length)
                frames.append(pcm_bytes)
                pcm = struct.unpack_from("h" * porcupine.frame_length, pcm_bytes)
                amplitude = rms(pcm)
                # Visualizer Pegel füttern
                QMetaObject.invokeMethod(MainWindow.visualizer, "feed_audio_level", Qt.ConnectionType.QueuedConnection, Q_ARG(float, min(amplitude / 1000.0, 1.0)))
                if amplitude < silence_threshold:
                    silence_frame_count += 1
                else:
                    silence_frame_count = 0
                if not MainWindow.recording_active:
                    log.info("Recording stopped due to button.")
                    break
                if silence_frame_count >= required_silence_frames:
                    log.info("Silence detected. Recording stopped.")
                    break

            # Visualizer Idle-Modus nach Aufnahme
            QMetaObject.invokeMethod(MainWindow.visualizer, "set_mode", Qt.ConnectionType.QueuedConnection, Q_ARG(str, "idle"))

            if frames:
                import tempfile
                temp_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
                audio_filepath = temp_file.name
                temp_file.close()
                wf = wave.open(audio_filepath, "wb")
                wf.setnchannels(1)
                wf.setsampwidth(pa.get_sample_size(pyaudio.paInt16))
                wf.setframerate(porcupine.sample_rate)
                wf.writeframes(b"".join(frames))
                wf.close()
                log.info(f"Recording saved under:{audio_filepath}")
                MainWindow.send_audio_to_server(audio_filepath)
        except Exception as e:
            log.info("Error in Wakeword Detection:{e}")
        finally:
            audio_stream.close()
            pa.terminate()
            porcupine.delete()
    threading.Thread(target=run_wakeword, daemon=True).start()
