from django.db import models


class Lock(models.Model):
    lock_name = models.CharField(max_length=255, unique=True)  # Tên lock
    lock_status = models.BooleanField(default=False)  # Trạng thái lock (True = locked, False = unlocked)
    created_at = models.DateTimeField(auto_now_add=True)  # Thời gian tạo lock
    updated_at = models.DateTimeField(auto_now=True)  # Thời gian cập nhật lock

    def __str__(self):
        return f"{self.lock_name} - {'Locked' if self.lock_status else 'Unlocked'}"
