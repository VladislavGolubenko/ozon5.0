# Generated by Django 3.2.7 on 2021-09-22 07:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0008_alter_product_ozon_product_id'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='product',
            options={'ordering': ['id'], 'verbose_name': 'товар', 'verbose_name_plural': 'товары'},
        ),
        migrations.AlterField(
            model_name='product',
            name='preview',
            field=models.CharField(max_length=300, verbose_name='Превью'),
        ),
    ]