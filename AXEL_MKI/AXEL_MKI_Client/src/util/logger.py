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

    # Datei-Handler (falls angegeben)
    if log_file:
        fh = logging.FileHandler(log_file)
        fh.setFormatter(formatter)
        logger.addHandler(fh)

    return logger

log = setup_logger("Axel-Client", "logs/programm.log")