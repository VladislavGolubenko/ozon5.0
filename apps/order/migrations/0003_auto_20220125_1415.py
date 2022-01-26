# Generated by Django 3.2.7 on 2022-01-25 14:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0002_auto_20220121_1426'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='order_sum',
            field=models.FloatField(blank=True, default=0, null=True, verbose_name='Сумма заказа'),
        ),
        migrations.AddField(
            model_name='order',
            name='quantity',
            field=models.IntegerField(blank=True, default=0, null=True, verbose_name='Количество'),
        ),
    ]
