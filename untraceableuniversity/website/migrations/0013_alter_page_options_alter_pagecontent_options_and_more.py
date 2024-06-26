# Generated by Django 4.2.4 on 2024-04-26 12:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0012_alter_page_options_page_position'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='page',
            options={'ordering': ['parent_page_id', 'position', 'name']},
        ),
        migrations.AlterModelOptions(
            name='pagecontent',
            options={'ordering': ['page__position', 'title']},
        ),
        migrations.RemoveField(
            model_name='page',
            name='slug',
        ),
    ]
