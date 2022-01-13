# Generated by Django 3.2.11 on 2022-01-13 14:52

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_number', models.CharField(max_length=500, verbose_name='Номер заказа')),
                ('date_of_order', models.DateTimeField(verbose_name='Дата и время размещения заказа')),
                ('in_process_at', models.DateTimeField(blank=True, null=True, verbose_name='Дата принятия в обработку')),
                ('status', models.CharField(blank=True, max_length=100, null=True, verbose_name='Статус заказ')),
                ('posting_number', models.CharField(blank=True, max_length=100, null=True, verbose_name='Номер отправления')),
                ('region', models.CharField(blank=True, max_length=500, null=True, verbose_name='Регион')),
                ('city', models.CharField(blank=True, max_length=500, null=True, verbose_name='Город')),
                ('delivery_type', models.CharField(blank=True, max_length=100, null=True, verbose_name='Тип доставки')),
                ('warehous_id', models.BigIntegerField(blank=True, null=True, verbose_name='ID склада')),
                ('warehouse_name', models.CharField(blank=True, max_length=500, null=True, verbose_name='Склад отгрузки')),
                ('creating_date', models.DateField(auto_now_add=True, null=True)),
                ('user_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='order_to_user', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'заказ',
                'verbose_name_plural': 'заказы',
                'ordering': ['id'],
            },
        ),
    ]
