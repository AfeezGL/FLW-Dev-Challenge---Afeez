# Generated by Django 3.1.3 on 2021-01-05 22:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0002_auto_20210105_2202'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='device_id',
            field=models.CharField(blank=True, max_length=30, null=True, unique=True),
        ),
    ]
