import sys
import os

def resource_path(relative_path):
    """
    Gibt den absoluten Pfad zu einer Ressource zurück,
    egal ob das Skript als exe gebündelt ist oder normal läuft.
    """
    if getattr(sys, 'frozen', False):
        # Programm läuft als exe (PyInstaller)
        base_path = sys._MEIPASS
    else:
        # Normaler Python-Run
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)
