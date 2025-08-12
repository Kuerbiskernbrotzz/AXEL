import socket
import tempfile
import threading
import time
import os
from PyQt6.QtCore import QMetaObject, Qt, Q_ARG
from pydub import AudioSegment
from util.config import SERVER_ADDRESS, PORT, PASSWORD
from .logger import log

log.info("audio handling initialized.")

def send_audio_to_server(main_window, audio_file):
    """
    Sends the audio file to the server and receives
    transcription, answer as text and answer as audio file
    """
    def run_audio_client():
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((SERVER_ADDRESS, main_window.audio_port))
                with open(audio_file, "rb") as f:
                    audio_bytes = f.read()

                s.sendall(f"AUTH {PASSWORD}\n".encode())
                s.recv(1024)
                s.sendall("AUDIO audio\n".encode())
                s.recv(1024)
                s.sendall(audio_bytes)
                s.sendall(b"<END>")

                # Receive transcribed user request
                transcript_data = b""
                while b"\n<TRANSCRIPT_END>\n" not in transcript_data:
                    part = s.recv(1024)
                    if not part:
                        break
                    transcript_data += part
                transcript_text = transcript_data.decode().replace("\n<TRANSCRIPT_END>\n", "")
                log.info(f"Request transcription: {transcript_text}")
                main_window.create_message_safe(
                    "User",
                    transcript_text,
                    Qt.AlignmentFlag.AlignRight,
                    "#2E86C1",
                    "#FFFFFF"
                )

                # Receive AI response
                ai_data = b""
                while b"\n<AI_END>\n" not in ai_data:
                    part = s.recv(1024)
                    if not part:
                        break
                    ai_data += part
                global ai_text
                ai_text = ai_data.decode().replace("\n<AI_END>\n", "")

                # Receive audio response
                audio_response = b""
                while True:
                    chunk = s.recv(1024)
                    if not chunk:
                        break
                    if b"<END>" in chunk:
                        index = chunk.find(b"<END>")
                        audio_response += chunk[:index]
                        break
                    audio_response += chunk

                # Save MP3 response to temporary file
                temp_mp3 = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
                mp3_path = temp_mp3.name
                temp_mp3.close()
                with open(mp3_path, "wb") as f:
                    f.write(audio_response)

                # Convert MP3 to WAV (optional, if visualizer requires WAV)
                temp_wav = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
                wav_path = temp_wav.name
                temp_wav.close()
                audio = AudioSegment.from_mp3(mp3_path)
                audio.export(wav_path, format="wav")
                log.debug(f"Audio converted to WAV: {wav_path}")

                log.info(f"Text response from server: {ai_text}")
                main_window.create_message_safe(
                    "Assistant",
                    ai_text,
                    Qt.AlignmentFlag.AlignLeft,
                    "#E8E8E8",
                    "#000000"
                )

                # Set visualizer to visualize mode and play audio
                def play_audio():
                    main_window.visualizer.set_mode("visualize")
                    main_window.audio_player.play(wav_path)
                

                # Execute in UI thread
                QMetaObject.invokeMethod(
                    main_window,
                    "_execute_in_main",
                    Qt.ConnectionType.QueuedConnection,
                    Q_ARG(object, play_audio)
                )
                
                main_window.audio_player.wait_for_playback_finished()

                # Clean up temporary files after playback
                def cleanup_files():
                    time.sleep(0.5)  # Small additional delay
                    for temp_file in [mp3_path, wav_path, audio_file]:
                        for attempt in range(3):
                            try:
                                if os.path.exists(temp_file):
                                    os.remove(temp_file)
                                    log.debug(f"Deleted: {temp_file}")
                                    break
                            except PermissionError as e:
                                if attempt == 2:
                                    log.error(f"Error deleting {temp_file}: {e}")
                                else:
                                    log.warning(f"File {temp_file} still in use. Retrying in 0.2 seconds...")
                                    time.sleep(0.2)
                            except Exception as e:
                                log.error(f"Unexpected error deleting {temp_file}: {e}")
                                break
                    log.info("Temporary audio files cleaned up")
                
                threading.Thread(target=cleanup_files, daemon=True).start()

        except Exception as e:
            log.error(f"Error sending/receiving audio data: {e}")
            if main_window.recording_active:
                log.info("Restarting wake word detection after error...")
                main_window.start_wakeword_detection()
        finally:
            if main_window.recording_active:
                log.info("Restarting wake word detection...")
                main_window.start_wakeword_detection()
    threading.Thread(target=run_audio_client, daemon=True).start()
