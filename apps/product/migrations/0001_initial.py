# Generated by Django 3.2.7 on 2021-09-07 08:09

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('preview', models.ImageField(blank=True, upload_to='preview/%y/%m/%d/')),
                ('sku', models.CharField(max_length=100)),
                ('name', models.CharField(max_length=300)),
                ('days_for_production', models.IntegerField(blank=True, null=True)),
                ('hours_for_production', models.IntegerField(blank=True, null=True)),
                ('minutes_for_production', models.IntegerField(blank=True, null=True)),
                ('reorder_days_of_supply', models.IntegerField()),
                ('unit_price', models.IntegerField(default=0)),
                ('logistics_price', models.IntegerField(default=0)),
                ('additional_price', models.IntegerField(default=0)),
                ('summ_price', models.IntegerField(blank=True, null=True)),
            ],
        ),
    ]