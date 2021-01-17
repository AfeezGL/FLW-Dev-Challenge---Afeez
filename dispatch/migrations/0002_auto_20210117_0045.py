# Generated by Django 3.1.3 on 2021-01-17 00:45

from django.db import migrations, models
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    dependencies = [
        ('dispatch', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='dispatchrider',
            name='store',
        ),
        migrations.AddField(
            model_name='dispatchrider',
            name='account_number',
            field=models.IntegerField(default=1234567890),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='dispatchrider',
            name='bank',
            field=models.CharField(default='firstbank', max_length=50),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='dispatchrider',
            name='phone_number',
            field=phonenumber_field.modelfields.PhoneNumberField(default='+2348162302855', max_length=128, region=None),
            preserve_default=False,
        ),
    ]