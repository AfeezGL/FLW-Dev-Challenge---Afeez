# Generated by Django 3.1.3 on 2021-01-19 00:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0012_remove_store_dispatch_rider'),
        ('dispatch', '0005_auto_20210119_0026'),
    ]

    operations = [
        migrations.AddField(
            model_name='dispatchrider',
            name='country',
            field=models.CharField(choices=[('NG', 'Nigeria'), ('GH', 'Ghana'), ('KE', 'Kenya'), ('UK', 'United Kingdom')], default='NG', max_length=2),
        ),
        migrations.AddField(
            model_name='dispatchrider',
            name='store',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='store.store'),
        ),
    ]
