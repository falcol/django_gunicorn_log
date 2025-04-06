from django.db import models


class Lock(models.Model):
    lock_name = models.CharField(max_length=255, unique=True)  # Tên lock
    is_lock = models.BooleanField(default=False)  # Trạng thái lock (True = locked, False = unlocked)
    locked_by_pid = models.IntegerField(null=True, blank=True)  # PID của process đang giữ lock
    lock_at = models.DateTimeField(auto_now_add=True, null=True)  # Thời gian tạo lock
    lock_updated_at = models.DateTimeField(auto_now=True)  # Thời gian cập nhật lock

    def __str__(self):
        return f"{self.lock_name} - {'Locked' if self.lock_status else 'Unlocked'}"
