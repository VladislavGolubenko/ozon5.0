# Generated by Django 3.2.11 on 2022-01-25 09:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0038_alter_product_offer_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='is_visible',
            field=models.BooleanField(blank=True, null=True, verbose_name='Видимость товара'),
        ),
    ]
