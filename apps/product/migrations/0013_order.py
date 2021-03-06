# Generated by Django 3.2.7 on 2021-10-06 13:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0012_alter_product_reorder_days_of_supply'),
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=300, verbose_name='Название товара')),
                ('order_number', models.IntegerField(verbose_name='Номер заказа')),
                ('sku', models.CharField(max_length=100, verbose_name='SKU')),
                ('date_of_order', models.DateTimeField(verbose_name='Дата и время размещения заказа')),
                ('order_place', models.CharField(max_length=1000, verbose_name='Куда заказан товар')),
                ('shipping_warehouse', models.CharField(max_length=2000, verbose_name='Склад отгрузки')),
                ('number', models.IntegerField(verbose_name='Количество')),
                ('price', models.IntegerField(verbose_name='Цена')),
                ('comission', models.IntegerField(verbose_name='Сумма комиссий')),
                ('profit', models.IntegerField(verbose_name='Прибыль')),
                ('status', models.CharField(max_length=100, verbose_name='Статус заказ')),
                ('linck_to_ozon', models.CharField(max_length=400, verbose_name='Посмотреть заказ в личном кабинете')),
            ],
            options={
                'verbose_name': 'заказ',
                'verbose_name_plural': 'товары',
                'ordering': ['id'],
            },
        ),
    ]
