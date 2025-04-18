# Generated by Django 5.1.7 on 2025-04-10 14:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("inventory", "0022_alter_accessory_return_status"),
    ]

    operations = [
        migrations.AlterField(
            model_name="accessory",
            name="return_status",
            field=models.CharField(
                blank=True,
                choices=[
                    ("In Use", "In Use"),
                    ("Returning", "Returning"),
                    ("Returned", "Returned"),
                ],
                default="In Use",
                max_length=20,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="accessory",
            name="status",
            field=models.CharField(
                blank=True,
                choices=[
                    ("Good", "Good"),
                    ("Needs Repair", "Needs Repair"),
                    ("Spoiled", "Spoiled"),
                ],
                default="Good",
                max_length=20,
                null=True,
            ),
        ),
    ]
