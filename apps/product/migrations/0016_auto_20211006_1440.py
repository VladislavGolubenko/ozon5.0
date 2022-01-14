# Generated by Django 3.2.7 on 2021-10-06 14:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0015_alter_order_price'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='comission',
            field=models.IntegerField(blank=True, null=True, verbose_name='Сумма комиссий'),
        ),
        migrations.AlterField(
            model_name='order',
            name='linck_to_ozon',
            field=models.CharField(blank=True, max_length=400, null=True, verbose_name='Посмотреть заказ в личном кабинете'),
        ),
        migrations.AlterField(
            model_name='order',
            name='order_place',
            field=models.CharField(blank=True, max_length=1000, null=True, verbose_name='Куда заказан товар'),
        ),
        migrations.AlterField(
            model_name='order',
            name='profit',
            field=models.IntegerField(blank=True, null=True, verbose_name='Прибыль'),
        ),
        migrations.AlterField(
            model_name='order',
            name='shipping_warehouse',
            field=models.CharField(blank=True, max_length=2000, null=True, verbose_name='Склад отгрузки'),
        ),
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Статус заказ'),
        ),
    ]