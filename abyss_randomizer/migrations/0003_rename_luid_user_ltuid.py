# Generated by Django 4.2 on 2023-06-01 14:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('abyss_randomizer', '0002_user_uid'),
    ]

    operations = [
        migrations.RenameField(
            model_name='user',
            old_name='luid',
            new_name='ltuid',
        ),
    ]