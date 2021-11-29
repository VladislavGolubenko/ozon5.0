# Generated by Django 3.2.7 on 2021-11-04 13:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('get_data', '0020_auto_20211006_1304'),
    ]

    operations = [
        migrations.CreateModel(
            name='Rate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rate_name', models.CharField(default='base', max_length=200, verbose_name='Название транзакции')),
                ('validity', models.IntegerField(verbose_name='Срок действия в днях')),
                ('price', models.FloatField(verbose_name='Стоимость тарифа')),
                ('description', models.CharField(max_length=1500, verbose_name='Краткое описание тарифа')),
            ],
            options={
                'verbose_name': 'тариф',
                'verbose_name_plural': 'тарифы',
                'ordering': ['id'],
            },
        ),
        migrations.AlterField(
            model_name='user',
            name='role',
            field=models.CharField(choices=[('user', 'user'), ('admin', 'admin'), ('subscription', 'subscription')], default='user', max_length=20, verbose_name='Роль'),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='rate',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='rate_transaction', to='get_data.rate', verbose_name='Тариф'),
        ),
    ]