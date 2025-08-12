from PyQt6.QtCore import QObject, QTimer

from .widget import AudioVisualizerWidget


class AudioVisualizerController(QObject):
    """
    Eine einfache Controller-Klasse, die AudioVisualizerWidget
    instanziiert und Methoden bereitstellt, um Modi zu schalten
    und (optional) kontinuierlich einen simulierten Audio-Level
    zu übergeben.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.widget = AudioVisualizerWidget(parent)
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._simulate_audio)

    def get_widget(self):
        return self.widget

    def set_idle(self):
        self._timer.stop()
        self.widget.set_mode("idle")

    def set_listening(self):
        self._timer.stop()
        self.widget.set_mode("listening")

    def set_visualize(self, simulate: bool = False):
        """
        Schaltet in den Visualize-Modus.
        Wenn simulate=True, wird alle 100 ms ein zufälliger Pegel
        übergeben.
        """
        self.widget.set_mode("visualize")
        if simulate:
            self._timer.start(100)

    def _simulate_audio(self):
        import random

        level = random.random()
        self.widget.feed_audio_level(level)
