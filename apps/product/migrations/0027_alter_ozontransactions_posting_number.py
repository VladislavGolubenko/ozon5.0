# Generated by Django 3.2.7 on 2021-11-03 14:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0026_alter_ozontransactions_operation_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ozontransactions',
            name='posting_number',
            field=models.CharField(max_length=500, verbose_name='Номер доставки'),
        ),
    ]
