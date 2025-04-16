from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    # Add custom fields here
    bio = models.TextField(blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)

    class Meta:
        verbose_name = "Custom User"
        verbose_name_plural = "Custom Users"
        db_table = "custom_user"  # Specify the database table name if needed

    def __str__(self):
        return self.username


class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField()
    u_date = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"
        db_table = "product"

    def __str__(self):
        return self.name
