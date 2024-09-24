import logging
import os
from logging.handlers import RotatingFileHandler

def setup_logging(log_path: str):
    os.makedirs(log_path, exist_ok=True)
    log_file = os.path.join(log_path, "card.log")
    
    class FlushFileHandler(logging.FileHandler):
        def emit(self, record):
            super().emit(record)
            self.flush()
    
    file_handler = FlushFileHandler(log_file, encoding="utf-8")
    console_handler = logging.StreamHandler()

    file_handler.setLevel(logging.INFO)
    console_handler.setLevel(logging.INFO)

    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    logger.handlers = []
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)