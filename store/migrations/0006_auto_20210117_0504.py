# Generated by Django 3.1.3 on 2021-01-17 05:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0005_auto_20210117_0351'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('PE', 'Pending'), ('SR', 'Sorting'), ('SH', 'Shipping'), ('DE', 'Delivered')], default='PE', max_length=2),
        ),
    ]