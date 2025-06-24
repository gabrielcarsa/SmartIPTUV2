from decimal import Decimal
import json
import re
from django import forms
from customer_suppliers.models import CustomerSupplier
from financials.models import AccountHolder, CheckingAccount, FinancialCategory, FinancialMovement, FinancialTransaction, FinancialTransactionInstallment
from django.core.validators import MinValueValidator

# Helper function to clean numbers (remove non-digit characters)
def clean_number(value):
    return re.sub(r'\D', '', value or '')

# Base class for form validation (boostrap, clean masks)
class BaseForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Define class bootstrap for all fields without overwriting other classes
        for field in self.fields:
            existing_classes = self.fields[field].widget.attrs.get('class', '')
            self.fields[field].widget.attrs['class'] = f"{existing_classes} form-control".strip()

        
    def add_invalid_class(self):
        # If form has errors, add 'is-invalid' class
        for field in self.errors:
            if field in self.fields:
                self.fields[field].widget.attrs['class'] += ' is-invalid'

    # Clean phone fields to ensure they contain 10 or 11 digits
    def clean_phone(self, field_name):
        phone = clean_number(self.cleaned_data.get(field_name))
        if phone and len(phone) not in [10, 11]:
            raise forms.ValidationError(f'O telefone {field_name} deve ter 10 ou 11 dígitos.')
        return phone

    # Generic method to clean CPF or CNPJ
    def clean_cpf_cnpj(self, field_name, length, error_message):
        value = clean_number(self.cleaned_data.get(field_name))
        if value and len(value) != length:
            raise forms.ValidationError(error_message)
        return value
    
    def clean(self):
        # Call the parent's clean() method to validate form data
        cleaned_data = super().clean()
        self.add_invalid_class()  # Add invalid class after cleaning

        return cleaned_data
    
# ----------
# FINANCIAL TRANSACTIONS
# ----------------------

# Transaction Form 
class TransactionForm(BaseForm):

    class Meta:
        model = FinancialTransaction
        fields = ['type', 'description', 'installment_value', 'down_payment', 'due_date', 'number_of_installments', 'account_holder', 'financial_category', 'customer_supplier']
        widgets = {
            'description': forms.TextInput(attrs={'placeholder': 'Ex.: salário mensal...', 'autocomplete': 'off'}),
            'number_of_installments': forms.TextInput(attrs={'placeholder': 'Ex.: 12', 'autocomplete': 'off'}),
            'due_date': forms.DateInput(attrs={'type': 'date'})
        }

    # define amount fields

    installment_value = forms.DecimalField(
        label='Valor da parcela',
        localize=True,  
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        widget=forms.TextInput(attrs={'class': 'money-mask'})
    )
    down_payment = forms.DecimalField(
        required=False,
        label='Valor da entrada (se houver)',
        localize=True,  
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        widget=forms.TextInput(attrs={'class': 'money-mask'})
    )

# Update amount field
class TransactionInstallmentAmountForm(forms.ModelForm):
    class Meta:
        model = FinancialTransactionInstallment
        fields = ['amount']

    amount = forms.DecimalField(
        label='Valor atualizado',
        localize=True,  
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        widget=forms.TextInput(attrs={'class': 'money-mask', 'placeholder': 'Digite o novo valor'})
    )

# Update amount field
class TransactionInstallmentDueDateForm(forms.ModelForm):
    class Meta:
        model = FinancialTransactionInstallment
        fields = ['due_date']
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date'})
        }

# Settlement installments
class TransactionInstallmentSettlementForm(BaseForm):
    class Meta:
        model = FinancialTransactionInstallment
        fields = ['payment_date', 'paid_amount']
        
    # Define the fields 'required'
    paid_amount = forms.DecimalField(
        required=True, 
        localize=True,  
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        widget=forms.TextInput(attrs={'placeholder': 'Ex.: 5.000,00', 'autocomplete': 'off', 'class': 'money-mask'})
    )
    payment_date = forms.DateField(required=True, widget=forms.DateInput(attrs={'type': 'date'}))



# Create ModelFormSet to update in bulk
TransactionInstallmentSettlementFormSet = forms.modelformset_factory(
    FinancialTransactionInstallment, 
    form=TransactionInstallmentSettlementForm,
    extra=0
)

# --------
# ACCOUNT HOLDERS
# ----------------

class AccountHolderForm(BaseForm):
    class Meta:
        model = AccountHolder
        fields = ['customer_supplier']

# ---------
# CHECKING ACCOUNT
# -----------------

class CheckingAccountForm(BaseForm):
    class Meta: 
        model = CheckingAccount
        fields = ['name', 'bank', 'account_number', 'agency', 'initial_balance']

# ----------
# FINANCIAL CATEGORY
# ------------------

class FinancialCategoryForm(BaseForm):
    class Meta:
        model = FinancialCategory
        fields = ['name']


# -----------
# FINANCIAL MOVEMENTS
# ---------------------

class OFXUploadForm(forms.Form):
    file = forms.FileField(label='Selecione o arquivo OFX')


class OFXMovementForm(BaseForm):

    class Meta:
        model = FinancialMovement
        fields = ['type', 'customer_supplier', 'category', 'description', 'amount', 'movement_date', 'transaction_installment']

    category = forms.ModelChoiceField(
        queryset=FinancialCategory.objects.all(),
        required=True,
        widget=forms.Select()
    )

    customer_supplier = forms.ModelChoiceField(
        queryset=CustomerSupplier.objects.all(),
        required=True,
        widget=forms.Select()
    )

    transaction_installment = forms.ModelChoiceField(
        queryset=FinancialTransactionInstallment.objects.filter(status=0,financial_transaction__type=0).order_by('due_date'),
        required=False,
        widget=forms.Select()
    )

MovimentsFormSet = forms.formset_factory(OFXMovementForm, extra=0, can_delete=True)

        
