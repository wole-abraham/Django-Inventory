# Generated by Django 5.1.3 on 2025-06-27 17:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0043_remove_equipmentsinsurvey_data_logger_serial_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='accessory',
            name='name',
            field=models.CharField(choices=[('tripod', 'Tripod'), ('levelling_staff', 'Levelling Staff'), ('GNSS Battery', 'GNSS Battery'), ('Pole', 'Pole'), ('Mini Prism', 'Mini Prism'), ('Sheet', 'Sheet'), ('Total Station prism', 'Total Station Prism'), ('Radio', 'Radio'), ('tracking_rod', 'Tracking Rod'), ('reflector', 'Reflector'), ('gps_extension_bar', 'GPS Extension Bar'), ('bar_port', 'Bar Port'), ('powerbank', 'Powerbank'), ('tribach', 'Tribach'), ('external_radio_antenna', 'External Radio Antenna'), ('Data Lpgger', 'Data Logger')], max_length=100),
        ),
    ]
