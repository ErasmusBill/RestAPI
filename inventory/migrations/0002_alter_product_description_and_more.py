# Generated by Django 5.1.4 on 2024-12-22 00:05

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='stock_quantity',
            field=models.PositiveIntegerField(blank=True, help_text='Current stock quantity', null=True, validators=[django.core.validators.MinValueValidator(0)]),
        ),
    ]
