# Generated by Django 5.1.6 on 2025-03-11 18:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('financials', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='checkingaccount',
            table='checking_accounts',
        ),
        migrations.AlterModelTable(
            name='checkingaccountbalance',
            table='checking_account_balances',
        ),
        migrations.AlterModelTable(
            name='financialcategory',
            table='financial_categories',
        ),
        migrations.AlterModelTable(
            name='financialmovement',
            table='financial_movements',
        ),
        migrations.AlterModelTable(
            name='financialtransaction',
            table='financial_transactions',
        ),
        migrations.AlterModelTable(
            name='financialtransactioninstallment',
            table='financial_transaction_installments',
        ),
    ]
