# Generated by Django 4.2.4 on 2023-11-03 05:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0006_discipline_alter_inspiration_options_question'),
    ]

    operations = [
        migrations.AddField(
            model_name='pagecontent',
            name='last_update',
            field=models.DateTimeField(auto_now=True),
        ),
    ]