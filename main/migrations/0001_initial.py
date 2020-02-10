# Generated by Django 2.2.10 on 2020-02-10 06:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Route',
            fields=[
                ('route_type', models.CharField(max_length=20)),
                ('route_id', models.CharField(max_length=30, primary_key=True, serialize=False)),
                ('route_number', models.CharField(max_length=30)),
                ('start_station_name', models.CharField(max_length=30)),
                ('end_station_name', models.CharField(max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name='Station',
            fields=[
                ('station_id', models.CharField(max_length=30, primary_key=True, serialize=False)),
                ('station_name', models.CharField(max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name='StationOtherName',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('station_id', models.CharField(max_length=30)),
                ('other_station_name', models.CharField(max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name='Time',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time', models.TimeField()),
                ('route', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.Route')),
                ('station', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.Station')),
            ],
        ),
    ]
