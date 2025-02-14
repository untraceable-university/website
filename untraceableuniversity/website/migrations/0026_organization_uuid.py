# Generated by Django 4.2.4 on 2025-02-14 08:27

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0025_apikey_event_event_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='organization',
            name='uuid',
            field=models.UUIDField(default=uuid.uuid4, unique=True),
        ),
    ]
