# Generated by Django 4.2.4 on 2025-02-16 07:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0031_alter_organization_url'),
    ]

    operations = [
        migrations.AlterField(
            model_name='people',
            name='url',
            field=models.URLField(blank=True, max_length=1000, null=True),
        ),
    ]
