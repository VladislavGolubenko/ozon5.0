# Generated by Django 3.2.11 on 2022-01-24 09:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0037_product_offer_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='offer_id',
            field=models.CharField(max_length=100, null=True, verbose_name='артикул'),
        ),
    ]
