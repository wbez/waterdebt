# Generated by Django 3.2.5 on 2021-07-16 23:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Case',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nov', models.CharField(max_length=25, unique=True)),
                ('street_dir', models.CharField(max_length=5)),
                ('street_name', models.CharField(max_length=50)),
                ('zip_plus_four', models.IntegerField()),
                ('disposition', models.CharField(max_length=100)),
                ('admin_cost', models.IntegerField()),
                ('sanction_cost', models.IntegerField()),
                ('penalty', models.IntegerField()),
                ('respondent', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Property',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('full_address', models.CharField(max_length=100)),
                ('metered', models.BooleanField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Debt',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('full_address', models.CharField(max_length=100)),
                ('bad_debt_no', models.CharField(max_length=50)),
                ('debt_collector', models.CharField(max_length=100)),
                ('debt_date', models.DateField()),
                ('debt_amt', models.IntegerField()),
                ('penalty', models.IntegerField()),
                ('payment', models.IntegerField()),
                ('metered', models.BooleanField()),
                ('balance', models.IntegerField()),
                ('no_occurrences', models.IntegerField()),
                ('prop', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='debt.property')),
            ],
        ),
    ]
