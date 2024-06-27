# Generated by Django 5.0.1 on 2024-05-18 04:33

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0010_users_first_name_users_last_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Return',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reason', models.TextField()),
                ('return_date', models.DateTimeField(auto_now_add=True)),
                ('order_item', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='shop.orderitem')),
            ],
        ),
    ]
