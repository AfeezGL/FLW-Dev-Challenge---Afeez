# Generated by Django 3.1.3 on 2021-01-19 00:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dispatch', '0005_auto_20210119_0026'),
        ('store', '0010_store_currency'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='dispatch_rider',
        ),
        migrations.AddField(
            model_name='store',
            name='dispatch_rider',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='dispatch.dispatchrider'),
        ),
    ]
