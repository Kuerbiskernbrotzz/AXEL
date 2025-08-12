import wave
import pyaudio
import threading
import numpy as np
from PyQt6.QtCore import QObject, pyqtSignal

class AudioPlayer(QObject):
    playback_finished = pyqtSignal()
    audio_level = pyqtSignal(float)

    def __init__(self):
        super().__init__()
        self._volume = 1.0
        self._is_muted = False
        self._is_playing = False
        self._stop_flag = False
        self._playback_finished_event = threading.Event()  # Event hinzufügen

    def set_volume(self, volume: float):
        self._volume = max(0.0, min(1.0, volume))

    def set_muted(self, muted: bool):
        self._is_muted = muted

    def stop(self):
        self._stop_flag = True

    def play(self, wav_path: str):
        def play_audio():
            try:
                wf = wave.open(wav_path, 'rb')
                p = pyaudio.PyAudio()

                def callback(in_data, frame_count, time_info, status):
                    if self._stop_flag:
                        return (None, pyaudio.paComplete)
                    
                    data = wf.readframes(frame_count)
                    if len(data) == 0:
                        return (None, pyaudio.paComplete)

                    # Audio-Samples in numpy array konvertieren
                    samples = np.frombuffer(data, dtype=np.int16)
                    
                    # Lautstärke anpassen
                    if not self._is_muted:
                        samples = (samples * self._volume).astype(np.int16)
                    else:
                        samples = np.zeros_like(samples)

                    # RMS-Level berechnen und normalisieren (0.0-1.0)
                    if len(samples) > 0:
                        rms = np.sqrt(np.mean(samples.astype(np.float32)**2))
                        normalized_level = min(1.0, rms / 32768.0)  # 32768 = max int16
                        self.audio_level.emit(normalized_level)
                    
                    return (samples.tobytes(), pyaudio.paContinue)

                stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                              channels=wf.getnchannels(),
                              rate=wf.getframerate(),
                              output=True,
                              stream_callback=callback)

                self._is_playing = True
                self._stop_flag = False
                
                stream.start_stream()
                while stream.is_active() and not self._stop_flag:
                    pass

                stream.stop_stream()
                stream.close()
                wf.close()
                p.terminate()
                
                self._is_playing = False
                self._playback_finished_event.set()  # Event setzen
                self.playback_finished.emit()
                
            except Exception as e:
                print("Fehler bei der Audio-Wiedergabe:", e)
                self._playback_finished_event.set()  # Event auch bei Fehler setzen
                self.playback_finished.emit()

        self._playback_finished_event.clear()  # Event zurücksetzen
        self._thread = threading.Thread(target=play_audio, daemon=True)
        self._thread.start()

    def wait_for_playback_finished(self, timeout=None):
        """Wartet, bis die Wiedergabe abgeschlossen ist."""
        self._playback_finished_event.wait(timeout)