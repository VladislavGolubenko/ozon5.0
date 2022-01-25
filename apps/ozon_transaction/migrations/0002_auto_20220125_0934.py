# Generated by Django 3.2.11 on 2022-01-25 09:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ozon_transaction', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='ozontransactions',
            name='is_visible',
            field=models.BooleanField(default=True, verbose_name='Видимость товара'),
        ),
        migrations.AddField(
            model_name='ozontransactions',
            name='marketplace_id',
            field=models.IntegerField(blank=True, null=True, verbose_name='ID маркетплейса'),
        ),
    ]
