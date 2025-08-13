import logging
import os
from pathlib import Path

def setup_logger(name: str, level=logging.INFO):
    """Creates and configures a logger with console and file output."""
    
    # Log-Verzeichnis im User-Verzeichnis anlegen
    log_dir = Path(os.path.expanduser('~')) / 'AppData' / 'Local' / 'AXEL-Client' / 'logs'
    log_dir.mkdir(parents=True, exist_ok=True)
    
    log_file = log_dir / 'programm.log'
    
    # Alte Log-Datei entfernen, falls vorhanden
    if log_file.exists():
        log_file.unlink()
    
    # Logger erzeugen
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.propagate = False  # Verhindert doppelte Logs, falls Root-Logger existiert

    # Format definieren
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

    # Konsolen-Handler
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    # Datei-Handler mit UTF-8 Encoding
    fh = logging.FileHandler(log_file, encoding='utf-8')
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    return logger

# Logger erstellen
log = setup_logger("Client")

# Beispiel:
log.info("Logger erfolgreich initialisiert.")
