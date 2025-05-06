from django.db import models
from django.contrib.auth.models import User
from customer_suppliers.models import CustomerSupplier

class AccountHolder(models.Model):

    customer_supplier = models.ForeignKey(CustomerSupplier,verbose_name='Cliente / Fornecedor', on_delete=models.SET_NULL, null=True, blank=True, related_name="account_holders")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='account_holder_user_created', verbose_name="Criado por")
    updated_by_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='account_holder_user_updated', verbose_name="Atualizado por")
    
    class Meta:
        verbose_name = 'Titular conta'
        db_table = 'account_holders'

    def __str__(self):
        return f"{self.customer_supplier}"
    

class CheckingAccount(models.Model):
    name = models.CharField("Nome", max_length=100)
    bank = models.CharField("Banco", max_length=50)
    account_holder = models.ForeignKey(AccountHolder, on_delete=models.CASCADE, related_name="checking_accounts")
    initial_balance = models.DecimalField("Saldo inicial", max_digits=10, decimal_places=2)
    agency = models.CharField("Agência", max_length=50)
    account_number = models.CharField("Número da conta", max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='checking_account_user_created', verbose_name="Criado por")
    updated_by_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='checking_account_user_updated', verbose_name="Atualizado por")

    class Meta:
        verbose_name = 'Contas Corrente'
        db_table = 'checking_accounts'
    
    def __str__(self):
        return f"{self.account_holder.customer_supplier.name}: {self.name}"


class CheckingAccountBalance(models.Model):
    checking_account = models.ForeignKey(CheckingAccount, on_delete=models.CASCADE, related_name="balances")
    balance = models.DecimalField(max_digits=10, decimal_places=2)
    balance_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Saldo'
        db_table = 'checking_account_balances'

    def __str__(self):
        return f"Saldo {self.balance} em {self.balance_date}"


class FinancialCategory(models.Model):
    EXPENSE = 0
    INCOME = 1
    CATEGORY_TYPE_CHOICES = [
        (EXPENSE, "Despesa"),
        (INCOME, "Receita"),
    ]

    type = models.BooleanField('Tipo', choices=CATEGORY_TYPE_CHOICES)
    is_default = models.BooleanField(default=False)
    name = models.CharField('Nome da categoria', max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='financial_category_user_created', verbose_name="Criado por")
    updated_by_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='financial_category_user_updated', verbose_name="Atualizado por")

    class Meta:
        verbose_name = 'Financeiro Categoria'
        db_table = 'financial_categories'

    def __str__(self):
        return self.name

class FinancialTransaction(models.Model):
    PAYABLE = 0
    RECEIVABLE = 1
    TRANSACTION_TYPE_CHOICES = [
        (PAYABLE, "A pagar"),
        (RECEIVABLE, "A receber"),
    ]

    type = models.BooleanField('Tipo', choices=TRANSACTION_TYPE_CHOICES)
    description = models.CharField('Descrição', max_length=255, null=True, blank=True)
    installment_value = models.DecimalField('Valor da parcela', max_digits=10, decimal_places=2)
    down_payment = models.DecimalField('Valor entrada (se houver)', max_digits=10, decimal_places=2, blank=True, null=True, default=0)
    due_date = models.DateField('Data de vencimento')
    number_of_installments = models.IntegerField('número de parcela')
    account_holder = models.ForeignKey(AccountHolder, on_delete=models.CASCADE, related_name="financial_transactions", verbose_name="Titular da conta")
    financial_category = models.ForeignKey(FinancialCategory, on_delete=models.CASCADE, related_name="transactions", verbose_name="Categorias")
    customer_supplier = models.ForeignKey(CustomerSupplier, on_delete=models.SET_NULL, null=True, blank=True, related_name="transactions", verbose_name="Cliente / Fornecedor")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='financial_transaction_user_created', verbose_name="Criado por")
    updated_by_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='financial_transaction_user_updated', verbose_name="Atualizado por")
    
    class Meta:
        verbose_name = 'Financeiro Conta'
        db_table = 'financial_transactions'

    def __str__(self):
        return f"{self.description} ({self.get_type_display()})"


class FinancialTransactionInstallment(models.Model):
    UNPAID = 0
    PAID = 1
    STATUS_CHOICES = [
        (UNPAID, "Não pago"),
        (PAID, "Pago"),
    ]

    financial_transaction = models.ForeignKey(FinancialTransaction, on_delete=models.CASCADE, related_name="installments")
    installment_number = models.IntegerField('Número parcela')
    amount = models.DecimalField('Valor', max_digits=10, decimal_places=2)
    due_date = models.DateField('Data de vencimento')
    payment_date = models.DateTimeField('Data de pagamento', null=True, blank=True)
    status = models.IntegerField(choices=STATUS_CHOICES, default=UNPAID)
    paid_amount = models.DecimalField('Valor pago', max_digits=10, decimal_places=2, null=True, blank=True)
    settlement_date = models.DateTimeField('Data baixa', null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    created_by_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='financial_transaction_installment_user_created', verbose_name="Criado por")
    updated_by_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='financial_transaction_installment_user_updated', verbose_name="Atualizado por")
    marked_down_by_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="marked_installments")

    class Meta:
        verbose_name = 'Financeiro Parcela'
        db_table = 'financial_transaction_installments'
    
    def __str__(self):
        return f"Parcela {self.installment_number} - {self.amount}"


class FinancialMovement(models.Model):
    OUTGOING = 0
    INCOMING = 1
    MOVEMENT_TYPE_CHOICES = [
        (OUTGOING, "Saída"),
        (INCOMING, "Entrada"),
    ]

    class Meta:
        verbose_name = 'Movimentações Financeira'
        db_table = 'financial_movements'

    checking_account = models.ForeignKey(CheckingAccount, on_delete=models.CASCADE, related_name="movements")
    financial_transaction_installment = models.ForeignKey(FinancialTransactionInstallment, on_delete=models.CASCADE, related_name="movements")
    type = models.BooleanField(choices=MOVEMENT_TYPE_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    movement_date = models.DateField()
    order = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='financial_movements_installment_user_created', verbose_name="Criado por")
    updated_by_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='financial_movements_installment_user_updated', verbose_name="Atualizado por")
   
    def __str__(self):
        return f"{self.get_type_display()} de {self.amount} em {self.movement_date}"

