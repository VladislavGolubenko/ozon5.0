# Generated by Django 3.2.11 on 2022-01-26 09:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0042_alter_productinorder_summ_price'),
    ]

    operations = [
        migrations.CreateModel(
            name='Categories',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category_id', models.IntegerField(verbose_name='ID категории')),
                ('name', models.CharField(max_length=255, verbose_name='Название')),
            ],
        ),
        migrations.AddField(
            model_name='product',
            name='fbo_deliv_to_customer_amount',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='product',
            name='fbo_direct_flow_trans_max_amount',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='product',
            name='fbo_direct_flow_trans_min_amount',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='product',
            name='fbo_fulfillment_amount',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='product',
            name='lower_range_limit',
            field=models.FloatField(default=0, verbose_name='Нижняя граница диапазона'),
        ),
        migrations.AddField(
            model_name='product',
            name='sales_percent',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='product',
            name='upper_range_limit',
            field=models.FloatField(default=0, verbose_name='Верхняя граница диапазона'),
        ),
        migrations.AddField(
            model_name='product',
            name='volume_weight',
            field=models.FloatField(default=0, verbose_name='Вес'),
        ),
        migrations.AddField(
            model_name='product',
            name='category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='product.categories', verbose_name='Категория'),
        ),
    ]
