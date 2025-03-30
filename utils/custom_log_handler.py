import glob
import logging
import os
from datetime import datetime, timedelta

from concurrent_log_handler import ConcurrentRotatingFileHandler

logger = logging.getLogger("django")


class DailyConcurrentRotatingFileHandler(ConcurrentRotatingFileHandler):
    def __init__(self, filename, backupCount=7, encoding=None, formatter=None):
        self.log_dir = os.path.dirname(filename)
        self.log_name = os.path.basename(filename)
        self.formatter_date_match = "%Y-%m-%d"  # Chỉ giữ lại YYYY-MM-DD
        self.current_date = datetime.now().strftime(self.formatter_date_match)
        self.backupCount = backupCount  # Số ngày giữ log

        # Gọi constructor gốc với file log theo ngày
        log_filename = self.get_log_filename()
        super().__init__(log_filename, maxBytes=0, backupCount=backupCount, encoding=encoding)

        if formatter:
            self.setFormatter(formatter)

    def get_log_filename(self):
        """Tạo tên file log dựa trên ngày hiện tại"""
        return os.path.join(self.log_dir, f"{self.log_name}.{self.current_date}.log")

    def shouldRollover(self, record):
        """Kiểm tra nếu cần tạo file log mới theo ngày"""
        new_date = datetime.now().strftime(self.formatter_date_match)
        return new_date != self.current_date

    def doRollover(self):
        """Tạo file log mới khi ngày thay đổi"""
        self.current_date = datetime.now().strftime(self.formatter_date_match)
        new_log_filename = self.get_log_filename()

        # Đóng file stream hiện tại trước khi đổi file
        self.close()

        # Đổi file log
        self.baseFilename = new_log_filename
        self.stream = self._open()

        # Xóa các file log cũ
        self.cleanup_old_logs()

    def cleanup_old_logs(self):
        """Xóa file log cũ hơn backupCount ngày + xóa file lock tương ứng"""
        if not os.path.exists(self.log_dir):
            logging.error(f"Log directory does not exist: {self.log_dir}")
            return

        log_pattern = os.path.join(self.log_dir, f"{self.log_name}.*.log")
        found_logs = glob.glob(log_pattern)

        if not found_logs:
            logging.warning(f"No log files found in: {self.log_dir}")
            return

        logging.info(f"Found log files: {found_logs}")

        # Xóa theo ngày
        cutoff_datetime = datetime.now() - timedelta(days=self.backupCount)

        for log_file in found_logs:
            try:
                timestamp_str = log_file.rsplit('.', 2)[-2]  # "2025-03-30"
                log_datetime = datetime.strptime(timestamp_str, self.formatter_date_match)

                if log_datetime < cutoff_datetime:
                    # Tạo tên file lock tương ứng
                    lock_file = os.path.join(self.log_dir, f".__{os.path.basename(log_file).replace('.log', '.lock')}")

                    # Đóng handler trước khi xóa file hiện tại
                    if log_file == self.baseFilename:
                        self.close()
                        logger.removeHandler(self)

                    # Xóa file lock trước
                    self._delete_file(lock_file, "Deleted lock file: ")
                    self._delete_file(log_file, "Deleted log file: ")

            except ValueError as e:
                logging.error(f"Skipping file {log_file}: {e}")

    def _delete_file(self, file_path, message):
        """Hàm xóa file chung"""
        if os.path.exists(file_path):
            os.chmod(file_path, 0o777)
            os.remove(file_path)
            logging.info(f"{message}{file_path}")
