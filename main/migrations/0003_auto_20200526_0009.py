# Generated by Django 2.2.9 on 2020-05-25 15:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_auto_20200213_2118'),
    ]

    operations = [
        migrations.AddField(
            model_name='station',
            name='local_x',
            field=models.DecimalField(decimal_places=6, default=0, max_digits=9),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='station',
            name='local_y',
            field=models.DecimalField(decimal_places=6, default=0, max_digits=9),
            preserve_default=False,
        ),
    ]
