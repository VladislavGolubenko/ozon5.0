# Generated by Django 3.2.7 on 2022-01-14 11:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0002_auto_20220114_0807'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='avatar',
            field=models.ImageField(blank=True, max_length=500, null=True, upload_to='photos/%y/%m/%d/'),
        ),
    ]