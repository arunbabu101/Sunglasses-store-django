# Generated by Django 5.0.1 on 2024-05-20 06:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0012_alter_order_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='color',
            field=models.CharField(default='black', max_length=50),
        ),
        migrations.AddField(
            model_name='product',
            name='size',
            field=models.IntegerField(default=50),
        ),
    ]
