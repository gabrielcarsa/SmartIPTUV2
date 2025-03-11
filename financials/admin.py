from django.contrib import admin

from .models import CheckingAccount, CheckingAccountBalance, FinancialCategory, FinancialMovement, FinancialTransaction, FinancialTransactionInstallment

admin.site.register(CheckingAccount)
admin.site.register(CheckingAccountBalance)
admin.site.register(FinancialCategory)
admin.site.register(FinancialTransaction)
admin.site.register(FinancialTransactionInstallment)
admin.site.register(FinancialMovement)
