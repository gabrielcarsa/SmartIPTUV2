from django import forms
import django_filters

from customer_suppliers.models import CustomerSupplier
from .models import AccountHolder, CheckingAccount, FinancialCategory, FinancialMovement, FinancialTransaction, FinancialTransactionInstallment

# Filter Transaction Installments
class FinancialTransactionInstallmentFilter(django_filters.FilterSet):

    financial_category = django_filters.ModelChoiceFilter(
        queryset=FinancialCategory.objects.all(),
        label="Categoria",
        widget=forms.Select(attrs={"class": "form-control col"}),
        field_name='financial_transaction__financial_category'
    )

    type = django_filters.ChoiceFilter(
        field_name='financial_transaction__type',
        choices=FinancialTransaction.TRANSACTION_TYPE_CHOICES,
        label="Tipo (Pagar / Receber)",
        widget=forms.Select(attrs={"class": "form-control"}),
        required=True
    )

    customer_supplier = django_filters.ModelChoiceFilter(
        queryset=CustomerSupplier.objects.all(),
        label="Cliente/Forncedor",
        widget=forms.Select(attrs={"class": "form-control col"}),
        field_name='financial_transaction__customer_supplier'

    )
    account_holder = django_filters.ModelChoiceFilter(
        queryset=AccountHolder.objects.all(),
        label="Titular da conta",
        widget=forms.Select(attrs={"class": "form-control"}),
        field_name='financial_transaction__account_holder'
    )
    id = django_filters.CharFilter(
        lookup_expr='exact',
        widget=forms.TextInput(attrs={"class": "form-control"})
    )

    start_date = django_filters.DateFilter(
        field_name='due_date',
        lookup_expr='gte',  # Greater Than or Equal
        label='Data Início',
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )

    end_date = django_filters.DateFilter(
        field_name='due_date',
        lookup_expr='lte',  # Less Than or Equal
        label='Data Fim',
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )


    class Meta:
        model = FinancialTransactionInstallment
        fields = ["type", "financial_category", "customer_supplier", "account_holder", "id", "start_date", "end_date"]

# Filter Movements
class FinancialMovementFilter(django_filters.FilterSet):

    movement_date__gte = django_filters.DateFilter(
        field_name='movement_date', 
        lookup_expr='gte',
        label='Data Início',
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        required=True
    )
    movement_date__lte = django_filters.DateFilter(
        field_name='movement_date', 
        lookup_expr='lte',
        label='Data Fim',
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        required=True
    )
    checking_account = django_filters.ModelChoiceFilter(
        queryset=CheckingAccount.objects.all(),
        field_name='checking_account',
        label="Conta corrente",
        widget=forms.Select(attrs={"class": "form-control"}),
        required=True
    )

    class Meta:
        model = FinancialMovement
        fields = ["movement_date__gte", "movement_date__lte", "checking_account"]