# Generated by Django 3.2.11 on 2022-01-13 14:52

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='PaymentType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(default='card', max_length=100, verbose_name='Способ оплаты')),
                ('description', models.CharField(max_length=1000, verbose_name='Описание способа оплаты')),
            ],
            options={
                'verbose_name': 'способ оплаты',
                'verbose_name_plural': 'способы оплаты',
                'ordering': ['type'],
            },
        ),
    ]
