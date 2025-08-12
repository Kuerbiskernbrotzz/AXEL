# src/voice_assistant_visualizer/widget.py

from pathlib import Path

from PyQt6.QtCore import QUrl, pyqtSignal, pyqtSlot
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEnginePage


class NoWarnWebEnginePage(QWebEnginePage):
    """
    WebEnginePage, die spezifische Three.js-Deprecation-Warnungen
    aus der JavaScript-Konsole herausfiltert.
    """

    def javaScriptConsoleMessage(self, level, message, lineNumber, sourceID):
        # Filtert genau die Meldung zu deprecated Scripts ab r150+
        if message.startswith('Scripts "') and 'are deprecated with r150+' in message:
            return
        super().javaScriptConsoleMessage(level, message, lineNumber, sourceID)


class AudioVisualizerWidget(QWebEngineView):

    def __init__(self, parent=None):
        super().__init__(parent)

        # Gefilterte Page, um Three.js-Warnungen zu unterdrücken
        self.setPage(NoWarnWebEnginePage(self))

        # Pfad zur lokalen HTML-Ressource
        base = Path(__file__).parent / "resources"
        html_path = base / "visualizer.html"
        self.load(QUrl.fromLocalFile(str(html_path.resolve())))
        self.setZoomFactor(1.0)

        # Flag und Queue für gepufferte JS-Befehle
        self._is_page_loaded = False
        self._pending_js = []

        # Lokalen Datei- und Remote-Zugriff erlauben
        settings = self.page().settings()
        settings.setAttribute(
            settings.WebAttribute.LocalContentCanAccessFileUrls, True
        )
        settings.setAttribute(
            settings.WebAttribute.LocalContentCanAccessRemoteUrls, True
        )

        # Lade-Signale verbinden
        self.loadStarted.connect(self._on_load_started)
        self.loadFinished.connect(self._on_load_finished)

        # Lautstärke und Stummschaltung
        self.volume = 1.0  # Standardlautstärke (0.0 - 1.0)
        self.is_muted = False

    def _on_load_started(self):
        """
        Wird ausgelöst, wenn die Seite neu lädt.
        Setzt das geladene-Flag zurück.
        """
        self._is_page_loaded = False

    def _on_load_finished(self, ok: bool):
        """
        Nach Abschluss des Ladens: führe alle gepufferten JS-Befehle aus.
        """
        self._is_page_loaded = True
        for js in self._pending_js:
            self.page().runJavaScript(js)
        self._pending_js.clear()

    def _run_js(self, js: str):
        """
        Puffer oder führe JavaScript aus, je nach Lade-Status.
        """
        if self._is_page_loaded:
            self.page().runJavaScript(js)
        else:
            self._pending_js.append(js)

    @pyqtSlot(str)
    def set_mode(self, mode: str):
        """
        Wechselt den Visualizer-Modus. Erlaubte Werte: 'idle', 'listening', 'visualize'.
        """
        self._run_js(f"setMode('{mode}');")

    @pyqtSlot(float)
    def feed_audio_level(self, level: float):
        """
        Übergibt einen normalisierten Audio-Pegel (0.0–1.0) an das Frontend.
        """
        self._run_js(f"feedAudioLevel({level});")

    @pyqtSlot(float)
    def set_volume(self, volume: float):
        """Setzt die Lautstärke (0.0 - 1.0)"""
        self.volume = max(0.0, min(1.0, volume))
        self._run_js(f"setVolume({self.volume});")

    @pyqtSlot(bool)
    def set_muted(self, muted: bool):
        """Schaltet die Audiowiedergabe stumm/an"""
        self.is_muted = muted
        self._run_js(f"setMuted({str(muted).lower()});")





