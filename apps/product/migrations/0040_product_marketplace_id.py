# Generated by Django 3.2.11 on 2022-01-25 09:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0039_product_is_visible'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='marketplace_id',
            field=models.IntegerField(blank=True, null=True, verbose_name='ID маркетплейса'),
        ),
    ]