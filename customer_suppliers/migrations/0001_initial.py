# Generated by Django 5.1.6 on 2025-03-11 17:15

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
            name='CustomerSupplier',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.IntegerField(choices=[(0, 'Cliente'), (1, 'Fornecedor'), (2, 'Ambos')])),
                ('name', models.CharField(max_length=100)),
                ('cnpj', models.CharField(blank=True, max_length=14, null=True, unique=True)),
                ('cpf', models.CharField(blank=True, max_length=11, null=True, unique=True)),
                ('phone', models.CharField(blank=True, max_length=11, null=True)),
                ('email', models.EmailField(blank=True, max_length=100, null=True)),
                ('street', models.CharField(blank=True, max_length=100, null=True)),
                ('neighborhood', models.CharField(blank=True, max_length=100, null=True)),
                ('number', models.CharField(blank=True, max_length=20, null=True)),
                ('complement', models.CharField(blank=True, max_length=100, null=True)),
                ('city', models.CharField(blank=True, max_length=100, null=True)),
                ('state', models.CharField(blank=True, max_length=100, null=True)),
                ('country', models.CharField(blank=True, max_length=100, null=True)),
                ('zip_code', models.CharField(blank=True, max_length=20, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='customer_supplier_user_created', to=settings.AUTH_USER_MODEL, verbose_name='Criado por')),
                ('updated_by_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='customer_supplier_user_updated', to=settings.AUTH_USER_MODEL, verbose_name='Atualizado por')),
            ],
        ),
    ]
