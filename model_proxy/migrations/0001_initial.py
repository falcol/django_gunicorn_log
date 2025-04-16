# Generated by Django 5.2 on 2025-04-16 13:16

import django.contrib.auth.models
from django.db import migrations


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('base_models', '0002_product_u_date'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomUserProxy',
            fields=[
            ],
            options={
                'verbose_name': 'Custom User Proxy',
                'verbose_name_plural': 'Custom User Proxies',
                'ordering': ['username'],
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('base_models.customuser',),
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='ProductProxy',
            fields=[
            ],
            options={
                'verbose_name': 'Product Proxy',
                'verbose_name_plural': 'Product Proxies',
                'ordering': ['name'],
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('base_models.product',),
        ),
    ]
