# Generated by Django 5.1.6 on 2025-03-13 10:48

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("tripnavigator", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RenameModel(
            old_name="UserProfile",
            new_name="User",
        ),
    ]
