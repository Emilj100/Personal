# Generated by Django 5.1.6 on 2025-03-25 15:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("tripnavigator", "0019_activity_travel_plan_day_travel_plan"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="activity",
            name="day",
        ),
        migrations.AddField(
            model_name="activity",
            name="date",
            field=models.DateField(blank=True, null=True),
        ),
        migrations.DeleteModel(
            name="Day",
        ),
    ]
