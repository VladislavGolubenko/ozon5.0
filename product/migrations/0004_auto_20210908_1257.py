# Generated by Django 3.2.7 on 2021-09-08 12:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0003_auto_20210908_1154'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='deliveries',
        ),
        migrations.RemoveField(
            model_name='product',
            name='return_product',
        ),
        migrations.RemoveField(
            model_name='product',
            name='way_waryhous',
        ),
        migrations.CreateModel(
            name='WarehouseAccounting',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stock_balance', models.IntegerField(verbose_name='Остатки на складе')),
                ('history', models.IntegerField(verbose_name='История продаж')),
                ('average_order_speed', models.IntegerField(verbose_name='Средняя скорость заказа')),
                ('status', models.CharField(default='wait', max_length=100, verbose_name='Статус закааза')),
                ('reordering_date', models.DateTimeField(blank=True, null=True, verbose_name='Дата перезаказа')),
                ('need_to_order', models.IntegerField(verbose_name='Необбходимо заказать')),
                ('reorder_summ', models.IntegerField(verbose_name='Сумма перезаказа')),
                ('reorder_profit', models.IntegerField(verbose_name='Прибыль перезаказа')),
                ('stock_for_days', models.IntegerField(verbose_name='Запасов на дней')),
                ('deliveries', models.IntegerField(verbose_name='Количество поставляется')),
                ('return_product', models.IntegerField(verbose_name='Количество возвращаемых товаров')),
                ('way_to_warehous', models.IntegerField(verbose_name='В пути на склад')),
                ('stock_profit', models.IntegerField(verbose_name='Потенциальная выручка с остатков')),
                ('stock_price', models.IntegerField(verbose_name='Себестоимость остатков')),
                ('potential_profit', models.IntegerField(verbose_name='Потенциальная прибыль')),
                ('average_unit_profit', models.IntegerField(verbose_name='Средняя прибыль единицы товара')),
                ('product_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='product_and_warehouse', to='product.product')),
            ],
            options={
                'verbose_name': 'Складской учет',
                'verbose_name_plural': 'Складской учёт',
                'ordering': ['id'],
            },
        ),
    ]
