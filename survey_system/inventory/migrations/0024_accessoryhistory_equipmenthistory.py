# Generated by Django 5.1.7 on 2025-04-11 13:42

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("inventory", "0023_alter_accessory_return_status_alter_accessory_status"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="AccessoryHistory",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "action",
                    models.CharField(
                        choices=[
                            ("created", "Created"),
                            ("updated", "Updated"),
                            ("released", "Released"),
                            ("returned", "Returned"),
                            ("status_changed", "Status Changed"),
                            ("image_uploaded", "Image Uploaded"),
                        ],
                        max_length=20,
                    ),
                ),
                (
                    "previous_status",
                    models.CharField(blank=True, max_length=20, null=True),
                ),
                ("new_status", models.CharField(blank=True, max_length=20, null=True)),
                (
                    "previous_return_status",
                    models.CharField(blank=True, max_length=20, null=True),
                ),
                (
                    "new_return_status",
                    models.CharField(blank=True, max_length=20, null=True),
                ),
                ("comment", models.TextField(blank=True, null=True)),
                ("changed_at", models.DateTimeField(auto_now_add=True)),
                (
                    "accessory",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="history",
                        to="inventory.accessory",
                    ),
                ),
                (
                    "changed_by",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="accessory_changes",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "new_chief_surveyor",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="new_accessory_history",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "previous_chief_surveyor",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="previous_accessory_history",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="EquipmentHistory",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "action",
                    models.CharField(
                        choices=[
                            ("created", "Created"),
                            ("updated", "Updated"),
                            ("released", "Released"),
                            ("returned", "Returned"),
                            ("status_changed", "Status Changed"),
                        ],
                        max_length=20,
                    ),
                ),
                (
                    "previous_status",
                    models.CharField(blank=True, max_length=20, null=True),
                ),
                ("new_status", models.CharField(blank=True, max_length=20, null=True)),
                ("comment", models.TextField(blank=True, null=True)),
                ("changed_at", models.DateTimeField(auto_now_add=True)),
                (
                    "changed_by",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="equipment_changes",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "equipment",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="history",
                        to="inventory.equipmentsinsurvey",
                    ),
                ),
                (
                    "new_chief_surveyor",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="new_equipment_history",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "previous_chief_surveyor",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="previous_equipment_history",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
