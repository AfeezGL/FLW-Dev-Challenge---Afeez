# Generated by Django 3.1.3 on 2021-01-17 00:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dispatch', '0002_auto_20210117_0045'),
        ('store', '0003_auto_20210115_0028'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='dispatch_rider',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='dispatch.dispatchrider'),
        ),
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('SH', 'Shipping'), ('DE', 'Delivered')], max_length=2, null=True),
        ),
    ]
