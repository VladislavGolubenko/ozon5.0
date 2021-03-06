# Generated by Django 3.2.11 on 2022-01-14 07:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('marketplace', '0003_marketplace_user'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='marketplace',
            name='last_validations_date',
        ),
        migrations.AlterField(
            model_name='marketplace',
            name='api_key',
            field=models.CharField(max_length=500, verbose_name='API ключ'),
        ),
        migrations.AlterField(
            model_name='marketplace',
            name='marketplace_id',
            field=models.IntegerField(verbose_name='ID пользователя маркетплейса'),
        ),
    ]
