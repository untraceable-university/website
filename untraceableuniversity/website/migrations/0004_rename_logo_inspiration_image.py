# Generated by Django 4.2.2 on 2023-08-25 16:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0003_inspiration'),
    ]

    operations = [
        migrations.RenameField(
            model_name='inspiration',
            old_name='logo',
            new_name='image',
        ),
    ]