# Generated by Django 3.1.3 on 2021-01-17 10:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0006_auto_20210117_0504'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='shipping_fee',
            field=models.IntegerField(default=0),
        ),
    ]
