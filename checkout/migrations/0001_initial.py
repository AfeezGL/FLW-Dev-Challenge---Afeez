# Generated by Django 3.1.3 on 2021-01-13 14:16

from django.db import migrations, models
import django.db.models.deletion
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('product', '0004_auto_20210106_1505'),
    ]

    operations = [
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=250, null=True)),
                ('last_name', models.CharField(max_length=250, null=True)),
                ('email', models.EmailField(blank=True, max_length=250, null=True)),
                ('address_line_1', models.CharField(max_length=250, null=True)),
                ('address_line_2', models.CharField(blank=True, max_length=250, null=True)),
                ('city', models.CharField(max_length=250, null=True)),
                ('state', models.CharField(max_length=250, null=True)),
                ('country', models.CharField(default='Nigeria', max_length=250)),
                ('postal_code', models.PositiveIntegerField(null=True)),
                ('phone_number', phonenumber_field.modelfields.PhoneNumberField(max_length=128, region=None)),
                ('order', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='product.order')),
            ],
        ),
    ]