import sys
import os
from pathlib import Path

def resource_path(relative_path):
    """Pfad zu einer Resource finden, egal ob dev oder PyInstaller"""
    if hasattr(sys, '_MEIPASS'):
        # Wenn in einer PyInstaller-Binary, aus _MEIPASS laden
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)
