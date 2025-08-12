import logging
import os

def setup_logger(name: str, log_file: str = None, level=logging.INFO):
    """Creates and configures a Logger with file-output."""
    if os.path.exists(log_file):
        os.remove(log_file)
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Format
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

    # Konsolen-Handler
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    # Datei-Handler (falls angegeben) mit UTF-8 Encoding
    if log_file:
        # Hier wird UTF-8 Encoding hinzugefügt
        fh = logging.FileHandler(log_file, encoding='utf-8')
        fh.setFormatter(formatter)
        logger.addHandler(fh)

    return logger

log = setup_logger("Axel-Client", "logs/programm.log")