from django.db import models
from django.contrib.auth.models import User

class CheckingAccount(models.Model):
    name = models.CharField(max_length=100)
    bank = models.CharField(max_length=50)
    initial_balance = models.DecimalField(max_digits=10, decimal_places=2)
    agency = models.CharField(max_length=50)
    account_number = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='checking_account_user_created', verbose_name="Criado por")
    updated_by_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='checking_account_user_updated', verbose_name="Atualizado por")

    def __str__(self):
        return f"{self.name} - {self.bank}"


class CheckingAccountBalance(models.Model):
    checking_account = models.ForeignKey(CheckingAccount, on_delete=models.CASCADE, related_name="balances")
    balance = models.DecimalField(max_digits=10, decimal_places=2)
    balance_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Saldo {self.balance} em {self.balance_date}"


class FinancialCategory(models.Model):
    EXPENSE = 0
    INCOME = 1
    CATEGORY_TYPE_CHOICES = [
        (EXPENSE, "Despesa"),
        (INCOME, "Receita"),
    ]

    type = models.BooleanField(choices=CATEGORY_TYPE_CHOICES)
    is_default = models.BooleanField(default=False)
    name = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='financial_category_user_created', verbose_name="Criado por")
    updated_by_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='financial_category_user_updated', verbose_name="Atualizado por")

    def __str__(self):
        return self.name

