import os
from datetime import datetime

from concurrent_log_handler import ConcurrentRotatingFileHandler


class DailyConcurrentRotatingFileHandler(ConcurrentRotatingFileHandler):
    def __init__(self, filename, backupCount=7, encoding=None, formatter=None):
        self.log_dir = os.path.dirname(filename)
        self.log_name = os.path.basename(filename)
        self.current_date = datetime.now().strftime("%Y-%m-%d-%H-%M")

        # Gọi constructor gốc với file tên mới theo ngày
        log_filename = self.get_log_filename()
        super().__init__(log_filename, maxBytes=0, backupCount=backupCount, encoding=encoding)

        if formatter:
            self.setFormatter(formatter)

    def get_log_filename(self):
        """Tạo tên file log dựa trên ngày hiện tại"""
        return os.path.join(self.log_dir, f"{self.log_name}.{self.current_date}.log")

    def shouldRollover(self, record):
        """Kiểm tra nếu cần tạo file log mới theo ngày"""
        new_date = datetime.now().strftime("%Y-%m-%d-%H-%M")
        return new_date != self.current_date

    def doRollover(self):
        """Tạo file log mới khi ngày thay đổi"""
        self.current_date = datetime.now().strftime("%Y-%m-%d-%H-%M")
        new_log_filename = self.get_log_filename()

        # Đóng file stream hiện tại
        if self.stream:
            self.stream.close()

        # Đổi file log
        self.baseFilename = new_log_filename
        self.stream = self._open()
