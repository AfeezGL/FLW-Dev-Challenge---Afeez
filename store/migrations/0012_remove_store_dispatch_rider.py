# Generated by Django 3.1.3 on 2021-01-19 00:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0011_auto_20210119_0030'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='store',
            name='dispatch_rider',
        ),
    ]
