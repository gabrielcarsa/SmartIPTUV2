# Generated by Django 5.1.6 on 2025-06-09 20:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('debits', '0003_alter_lot_bottom_confrontation_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='salescontract',
            name='installment_value',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Valor das parcelas'),
        ),
    ]
