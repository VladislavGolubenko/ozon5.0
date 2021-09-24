# Generated by Django 3.2.7 on 2021-09-08 12:57

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('get_data', '0006_auto_20210907_1326'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userpayment',
            name='id_user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='user_payment', to=settings.AUTH_USER_MODEL),
        ),
    ]
