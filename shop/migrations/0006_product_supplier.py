# Generated by Django 5.0.1 on 2024-04-30 13:04

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0005_order_status'),
        ('supplier', '0002_supplier_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='supplier',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='supplier.supplier'),
        ),
    ]
