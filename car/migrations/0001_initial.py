# Generated by Django 5.2.1 on 2025-05-17 15:00

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Car',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('make', models.CharField(choices=[('HONDA', 'Honda'), ('MAZDA', 'Mazda'), ('MITSUBISHI', 'Mitsubishi'), ('SUBARU', 'Subaru')], db_comment='The car brand', help_text='The car brand', max_length=50)),
                ('model', models.CharField(db_comment='The car model', help_text='The car model', max_length=50)),
                ('slug', models.SlugField(db_comment='Slugified combination of make and model', help_text='Slugified combination of make and model')),
                ('capacity', models.IntegerField(db_comment='The total passenger capacity', help_text='The total passenger capacity', unique=True)),
                ('transmission', models.CharField(choices=[('AT', 'Automatic'), ('MT', 'Manual')], db_comment='The car transmission', help_text='The car transmission')),
                ('drivetrain', models.CharField(choices=[('AWD', 'All Wheel Drive'), ('4WD', 'Four Wheel Drived'), ('FWD', 'Front Wheel Drive'), ('RWD', 'Rear Wheel Drive')], db_comment='The car drivetrain', help_text='The car drivetrain')),
                ('fuel_type', models.CharField(choices=[('B', 'Bensin'), ('G91', 'Gasohol 91'), ('G95', 'Gasohol 95'), ('GE20', 'Gasohol E20'), ('GE85', 'Gasohol E85'), ('PB', 'Premium Bensin')], db_comment='The car fuel type', help_text='The car fuel type')),
                ('fuel_consumption_metric', models.FloatField(db_comment='The fuel efficiency, represented in liters per 100km (L/100km)', help_text='The fuel efficiency, represented in liters per 100km (L/100km)')),
                ('engine_code', models.CharField(db_comment='The car engine identifier', help_text='The car engine identifier', max_length=12)),
                ('power_hp', models.IntegerField(db_comment='The engine power in HP', help_text='The engine power in HP')),
                ('power_max_rpm', models.IntegerField(db_comment='The engine max RPM for the given power', help_text='The engine max RPM for the given power')),
                ('price_hourly_cents', models.IntegerField(db_comment='The hourly rate of a rental, in cents', help_text='The hourly rate of a rental, in cents')),
                ('price_9_hours_cents', models.IntegerField(db_comment='The price for a 9 hours rental, in cents', help_text='The price for a 9 hours rental, in cents')),
                ('price_12_hours_cents', models.IntegerField(db_comment='The price for a 12 hours rental, in cents', help_text='The price for a 12 hours rental, in cents')),
                ('price_24_hours_cents', models.IntegerField(db_comment='The price for a 24 hours rental, in cents', help_text='The price for a 24 hours rental, in cents')),
                ('created_at', models.DateTimeField(db_comment='The creation date of the car object', default=django.utils.timezone.now, help_text='The creation date of the car object')),
                ('updated_at', models.DateTimeField(blank=True, db_comment='The last updated date of the car object', help_text='The last updated date of the car object', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='CarFeature',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(choices=[('AIR_BAGS', 'Air Bags'), ('AIR_CONDITIONING', 'Air Conditioning'), ('ABS', 'Anti Lock Breaking System'), ('ASSISTED_STEERING', 'Assisted Steering'), ('BLUETOOTH', 'Bluetooth'), ('DASH_CAM', 'Dash Cam'), ('DRIVE_MODES', 'Drive Modes'), ('ESC', 'Electronic Stability Control'), ('GPS_NAVIGATION', 'Gps Navigation'), ('KEYLESS_ENTRY', 'Keyless Entry'), ('LED_HEADLIGHTS', 'Led Headlights'), ('POP_UP_HEADLIGHTS', 'Pop Up Headlights'), ('POWERED_WINDOWS', 'Powered Windows'), ('REAR_CAMERA', 'Rear Camera'), ('USB_PORTS', 'Usb Ports')], db_comment='The name of the car feature', help_text='The name of the car feature', max_length=25, unique=True)),
                ('created_at', models.DateTimeField(db_comment='The creation date of the feature object', default=django.utils.timezone.now, help_text='The creation date of the feature object')),
            ],
        ),
        migrations.CreateModel(
            name='CarFeatureAssignment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='CarMedia',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.URLField(db_comment='The full path of the resource', help_text='The full path of the resource')),
                ('is_thumbnail', models.BooleanField(db_comment='When set to True, the media is used as the car thumbnail', help_text='When set to True, the media is used as the car thumbnail')),
                ('created_at', models.DateTimeField(db_comment='The creation date of the media object', default=django.utils.timezone.now, help_text='The creation date of the media object')),
            ],
        ),
    ]
