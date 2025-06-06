# Generated by Django 5.1.6 on 2025-03-12 17:57

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('financials', '0003_accountholder'),
    ]

    operations = [
        migrations.AddField(
            model_name='checkingaccount',
            name='account_holder',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='checking_accounts', to='financials.accountholder'),
            preserve_default=False,
        ),
    ]
