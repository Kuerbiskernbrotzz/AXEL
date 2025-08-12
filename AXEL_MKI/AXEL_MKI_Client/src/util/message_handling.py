import socket
import threading
from PyQt6.QtCore import Qt
from util.config import SERVER_ADDRESS, PORT, PASSWORD
from .logger import log

log.info("Message handling initialized.")
def send_text_to_server(main_window, text_input):
    """
    Sendet den Text aus dem messageInput an den Server, empfängt die Antwort
    und gibt diese im Terminal sowie im Chatverlauf aus.
    """
    if not text_input:
        log.info("No text found.")
        return

    main_window.ui.messageInput.clear()
    main_window.create_message_safe(
        "User", 
        text_input, 
        Qt.AlignmentFlag.AlignRight,
        "#2E86C1",  # Blau
        "#FFFFFF"   # Helle Schrift
    )

    def run_text_client():
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((SERVER_ADDRESS, int(PORT)))
            s.sendall(f"AUTH {PASSWORD}\n".encode())
            s.recv(1024)
            s.sendall(f"TEXT {text_input}\n".encode())
            reply = b""
            while b"\n<END>\n" not in reply:
                part = s.recv(1024)
                if not part:
                    break
                reply += part
            reply_str = reply.decode().replace("\n<END>\n", "")
            log.info(f"Text answer form the server: {reply_str}")
            main_window.create_message_safe(
                "Assistant", 
                reply_str, 
                Qt.AlignmentFlag.AlignLeft,
                "#E8E8E8",  # Hellgrau für den Assistant
                "#000000"   # Schwarze Schrift
            )
            s.close()
        except Exception as e:
            print("Error sending/recieving text-files:", e)
            return
    threading.Thread(target=run_text_client, daemon=True).start()

def clear_context(main_window):
    """
    Empties the chat-history in the scroll area
    and sends the COMMAND "/clear_context" to the server.
    """
    # UI-Elemente löschen
    while main_window.scroll_layout.count():
        item = main_window.scroll_layout.takeAt(0)
        widget = item.widget()
        if widget:
            widget.deleteLater()

    # Command an Server senden
    def run_clear_command():
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((SERVER_ADDRESS, int(PORT)))
                s.sendall(f"AUTH {PASSWORD}\n".encode())
                s.recv(1024)  # Warte auf Auth-Bestätigung
                s.sendall("COMMAND /clear_context\n".encode())
                response = s.recv(1024).decode().strip()
                log.info(f"server answer to clear_context: {response}")
        except Exception as e:
            log.info(f"error sending the clear conext Command: {e}")

    # Command in separatem Thread ausführen
    threading.Thread(target=run_clear_command, daemon=True).start()