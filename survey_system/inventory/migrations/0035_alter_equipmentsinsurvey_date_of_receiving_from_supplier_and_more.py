# Generated by Django 5.1.3 on 2025-06-19 13:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0034_alter_equipmentsinsurvey_project'),
    ]

    operations = [
        migrations.AlterField(
            model_name='equipmentsinsurvey',
            name='date_of_receiving_from_supplier',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='equipmentsinsurvey',
            name='project',
            field=models.CharField(blank=True, choices=[('Coastal Road', 'Coastal Road'), ('Sokoto', 'Sokoto')], max_length=20),
        ),
    ]
