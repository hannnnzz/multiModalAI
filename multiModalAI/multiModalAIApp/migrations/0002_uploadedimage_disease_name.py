# Generated by Django 5.2 on 2025-04-26 07:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("multiModalAIApp", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="uploadedimage",
            name="disease_name",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
