# Generated by Django 5.1.6 on 2025-03-11 15:34

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CheckingAccount',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('bank', models.CharField(max_length=50)),
                ('initial_balance', models.DecimalField(decimal_places=2, max_digits=10)),
                ('agency', models.CharField(max_length=50)),
                ('account_number', models.CharField(max_length=50)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='checking_account_user_created', to=settings.AUTH_USER_MODEL, verbose_name='Criado por')),
                ('updated_by_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='checking_account_user_updated', to=settings.AUTH_USER_MODEL, verbose_name='Atualizado por')),
            ],
        ),
        migrations.CreateModel(
            name='CheckingAccountBalance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('balance', models.DecimalField(decimal_places=2, max_digits=10)),
                ('balance_date', models.DateField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('checking_account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='balances', to='financial.checkingaccount')),
            ],
        ),
        migrations.CreateModel(
            name='FinancialCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.BooleanField(choices=[(0, 'Despesa'), (1, 'Receita')])),
                ('is_default', models.BooleanField(default=False)),
                ('name', models.CharField(max_length=50)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='financial_category_user_created', to=settings.AUTH_USER_MODEL, verbose_name='Criado por')),
                ('updated_by_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='financial_category_user_updated', to=settings.AUTH_USER_MODEL, verbose_name='Atualizado por')),
            ],
        ),
    ]
