from datetime import datetime
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path



class DailyRotatingFileHandler(RotatingFileHandler):
    def __init__(self, base_log_path, *args, **kwargs):
        self.base_log_path = Path(base_log_path)
        self.current_date = datetime.now().strftime("%Y/%m/%d")
        self._update_log_path()
        super().__init__(self.log_file, *args, **kwargs)

    def _update_log_path(self):
        log_path = self.base_log_path / self.current_date
        log_path.mkdir(parents=True, exist_ok=True)
        self.log_file = log_path / "sync.log"

    def emit(self, record):
        new_date = datetime.now().strftime("%Y/%m/%d")
        if new_date != self.current_date:
            self.current_date = new_date
            self._update_log_path()
            self.baseFilename = str(self.log_file)

        super().emit(record)
