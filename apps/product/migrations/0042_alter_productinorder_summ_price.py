# Generated by Django 3.2.11 on 2022-01-25 17:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0041_alter_product_is_visible'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productinorder',
            name='summ_price',
            field=models.FloatField(blank=True, default=0, null=True, verbose_name='Итого'),
        ),
    ]