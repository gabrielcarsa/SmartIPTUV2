from django.contrib import admin

from . import models

admin.site.register(models.CheckingAccount)
admin.site.register(models.CheckingAccountBalance)
admin.site.register(models.FinancialCategory)
admin.site.register(models.FinancialTransaction)
admin.site.register(models.FinancialTransactionInstallment)
admin.site.register(models.FinancialMovement)
admin.site.register(models.AccountHolder)

