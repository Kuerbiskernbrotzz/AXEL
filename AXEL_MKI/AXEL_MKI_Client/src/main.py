# Standardbibliotheken
import sys
import os
import warnings
from pathlib import Path
import logging


# Drittanbieter-Bibliotheken
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout,
    QHBoxLayout, QSizePolicy, QMainWindow
)
from PyQt6.QtCore import QTimer, Qt, QMetaObject, Q_ARG, pyqtSlot
import markdown

# Eigene Module
from util.App_ui import Ui_MainWindow
from util.config import *
from util.wakeword import start_wakeword_detection
from voice_assistant_visualizer.widget import AudioVisualizerWidget
from voice_assistant_visualizer.audio_player import AudioPlayer
from util.authentication import authenticate_with_server
from util.audio_handling import send_audio_to_server
from util.message_handling import send_text_to_server, clear_context
from util.logger import setup_logger

# Unterdrücke Qt Deprecation Warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)


class MainWindow(QMainWindow):
    """
    Main Window including Wakeword detection, authentication and chat history.
    """
    def __init__(self):
        super().__init__()
        self.audio_port = int(PORT)
        self.setup_ui()
        self.init_audio_system()
        self.connect_signals()
        self.setup_visualizer()
        self.audio_player = AudioPlayer()
        self.audio_player.playback_finished.connect(self.on_playback_finished)
        self.audio_player.audio_level.connect(self.on_audio_level)

    # ============================ UI Setup ===================================
    def setup_ui(self):
        """Initializes the UI-Components."""
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.messageInput.setStyleSheet("color: #D3D3D3;")
        self.setup_chat_history()

    def setup_chat_history(self):
        """Initializes the Chat History."""
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll_layout.setSpacing(5)
        self.ui.chatHistory.setWidget(self.scroll_content)

    def setup_visualizer(self):
        # Visualizer-Widget referenzieren
        self.visualizer = self.ui.audioVisualizer
        self.visualizer.set_mode("idle")
        # Lautstärke initialisieren
        self.visualizer.set_volume(self.ui.volumeSlider.value() / 100.0)
        self.visualizer.set_muted(not self.ui.volumeButton.isChecked())
        # Lautstärke-Slider verbinden
        self.ui.volumeSlider.valueChanged.connect(self.on_volume_changed)
        self.ui.volumeButton.toggled.connect(self.on_volume_mute_toggled)

    def on_volume_changed(self, value):
        volume = value / 100.0
        self.audio_player.set_volume(volume)
        self.visualizer.set_volume(volume)

    def on_volume_mute_toggled(self, checked):
        self.audio_player.set_muted(not checked)
        self.visualizer.set_muted(not checked)

    @pyqtSlot()
    def on_playback_finished(self):
        self.visualizer.set_mode("idle")

    @pyqtSlot(float)
    def on_audio_level(self, level):
        self.visualizer.feed_audio_level(level)

    def init_audio_system(self):
        """Initializes the audio System."""
        self.recording_active = True
        self.ui.micButton.setChecked(True)
        self.start_wakeword_detection()

    def connect_signals(self):
        """Connects all Signal-Slots."""
        QTimer.singleShot(100, self.authenticate_with_server)
        self.ui.micButton.clicked.connect(self.on_mic_clicked)
        self.ui.sendButton.clicked.connect(self.send_text_to_server)
        self.ui.messageInput.returnPressed.connect(self.send_text_to_server)
        self.ui.clearContextButton.clicked.connect(self.clear_context)
        self.ui.settingsButton.clicked.connect(self.open_settings)

    # ============================ UI Message Creation ========================
    def create_message_safe(self, name, text, align, bg_color="#e0e0e0", text_color="#000000"):
        """Threading-Secure Method for creating messages in the UI-Thread."""
        QMetaObject.invokeMethod(
            self,
            "_create_message_impl",
            Qt.ConnectionType.QueuedConnection,
            Q_ARG(str, name),
            Q_ARG(str, text),
            Q_ARG(Qt.AlignmentFlag, align),
            Q_ARG(str, bg_color),
            Q_ARG(str, text_color)
        )

    @pyqtSlot(str, str, Qt.AlignmentFlag, str, str)
    def _create_message_impl(self, name: str, text: str, align: Qt.AlignmentFlag,
                             bg_color: str = "#e0e0e0", text_color: str = "#000000"):
        """Creates and inputs the Message in the Chat-History."""
        # Wrapper für Links-/Rechtsausrichtung
        wrapper = QWidget()
        h_layout = QHBoxLayout(wrapper)
        h_layout.setContentsMargins(0, 0, 0, 0)

        # Nachrichtenkasten
        message_box = QWidget()
        v_layout = QVBoxLayout(message_box)
        v_layout.setContentsMargins(8, 6, 8, 6)
        v_layout.setSpacing(4)

        # Überschrift (Name) klar vom Text trennen
        name_label = QLabel(name)
        name_label.setStyleSheet(f"color: {text_color}; font-weight: bold; padding: 4px; border-bottom: 1px solid #CCCCCC;")
        name_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        v_layout.addWidget(name_label)

        # Nachrichtentext: Markdown in HTML konvertieren
        converted_text = markdown.markdown(text)
        message_label = QLabel(converted_text)
        message_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        message_label.setTextFormat(Qt.TextFormat.RichText)
        message_label.setStyleSheet(f"color: {text_color};")
        message_label.setWordWrap(True)
        message_label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)
        v_layout.addWidget(message_label)

        # Style & Verhalten für den Nachrichtenkasten
        message_box.setStyleSheet(f"background-color: {bg_color}; border-radius: 8px;")
        message_box.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
        # Max. Breite beschränken (75 % der Fensterbreite)
        message_box.setMaximumWidth(int(self.width() * 0.75))

        # Nachricht in Ausrichtungs-Wrapper einfügen
        h_layout.addStretch() if align == Qt.AlignmentFlag.AlignRight else None
        h_layout.addWidget(message_box)
        h_layout.addStretch() if align == Qt.AlignmentFlag.AlignLeft else None

        self.scroll_layout.addWidget(wrapper)

        # Layout und Chatbereich aktualisieren
        self.scroll_content.adjustSize()
        self.ui.chatHistory.update()
        QApplication.processEvents()
        self.ui.chatHistory.verticalScrollBar().setValue(self.ui.chatHistory.verticalScrollBar().maximum())

    # ============================ Server Authentifizierung ====================
    def authenticate_with_server(self):
        """authenticate with server"""
        authenticate_with_server()

    # ============================ Wakeword Detection ==========================
    def on_mic_clicked(self):
        """Starts or stopps the Wakeword detection based on the Mic-Button-State."""
        if self.ui.micButton.isChecked():
            log.info("Wakeword Detection started...")
            self.recording_active = True
            self.start_wakeword_detection()
        else:
            log.info("Wakeword Detection stopped.")
            self.recording_active = False

    def start_wakeword_detection(self):
        start_wakeword_detection(self)

    # ============================ Audio-Handling ==============================
    def send_audio_to_server(self, audio_file):
        send_audio_to_server(self, audio_file)

    # ============================ Textnachrichten ==================================
    def send_text_to_server(self):
        text_input = self.ui.messageInput.text()
        send_text_to_server(self, text_input)

    # ============================ Clear Context ===================================
    def clear_context(self):
        clear_context(self)

    # ============================ Settings öffnen ===============================
    def open_settings(self):
        """Openes the Settings-file-path in the File Explorer"""
        settings_path = os.path.join(os.path.dirname(__file__), "settings")
        os.startfile(settings_path)

    # ============================ Hilfsmethoden ===============================
    @pyqtSlot(object)
    def _execute_in_main(self, func):
        """runs a function in the ui thread"""
        func()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
    
#Made by Kürbiskernbrot