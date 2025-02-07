# Generated by Django 5.1.5 on 2025-02-03 09:23

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_driver_remove_user_account_account_last_credit_reset_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='driver',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='drivers', to=settings.AUTH_USER_MODEL),
        ),
    ]
