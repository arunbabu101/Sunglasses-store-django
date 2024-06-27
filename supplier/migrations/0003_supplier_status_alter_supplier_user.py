# Generated by Django 5.0.1 on 2024-05-15 13:46

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('supplier', '0002_supplier_user'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='supplier',
            name='status',
            field=models.CharField(default='active', max_length=20),
        ),
        migrations.AlterField(
            model_name='supplier',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
