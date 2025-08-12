"""
voice_assistant_visualizer
--------------------------

Eine PyQt6-Library, die ein Web-Widget bereitstellt,
in dem ein futuristischer 3D-Audio-Visualizer läuft.
"""

__version__ = "0.1.0"

from .widget import AudioVisualizerWidget
from .controller import AudioVisualizerController

__all__ = [
    "AudioVisualizerWidget",
    "AudioVisualizerController",
]
