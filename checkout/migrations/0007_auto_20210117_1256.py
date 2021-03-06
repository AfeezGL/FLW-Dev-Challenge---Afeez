# Generated by Django 3.1.3 on 2021-01-17 12:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0007_order_shipping_fee'),
        ('checkout', '0006_auto_20210117_1209'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderdetails',
            name='cart_total',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='orderdetails',
            name='order',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='details', to='store.order'),
        ),
        migrations.AlterField(
            model_name='orderdetails',
            name='shipping_total',
            field=models.IntegerField(default=0),
        ),
    ]
