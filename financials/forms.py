from decimal import Decimal
import re
from django import forms

from financials.models import AccountHolder, FinancialTransaction, FinancialTransactionInstallment

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
    
    # Clean money field replace to save
    def clean_money_field(self, field_name):
        value = self.cleaned_data.get(field_name)

        if value:
            try:            
                value = value.replace(',', '.')
                return value
            except ValueError:
                raise forms.ValidationError("Valor inválido!")

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
            'installment_value': forms.TextInput(attrs={'placeholder': 'Ex.: 2.500,00', 'autocomplete': 'off'}),
            'down_payment': forms.TextInput(attrs={'placeholder': 'Ex.: 5.000,00 (se houver)', 'autocomplete': 'off'}),
            'number_of_installments': forms.TextInput(attrs={'placeholder': 'Ex.: 12', 'autocomplete': 'off'}),
            'installment_value': forms.TextInput(attrs={'placeholder': 'Ex.: 2.500,00', 'autocomplete': 'off'}),
            'due_date': forms.DateInput(attrs={'type': 'date'})
        }


# Update amount field
class TransactionInstallmentAmountForm(forms.ModelForm):
    class Meta:
        model = FinancialTransactionInstallment
        fields = ['amount']
        widgets = {
            'amount': forms.TextInput(attrs={'placeholder': 'Ex.: 1.500,00', 'autocomplete': 'off'}),
        }


# Settlement installments
class TransactionInstallmentSettlementForm(BaseForm):
    class Meta:
        model = FinancialTransactionInstallment
        fields = ['payment_date', 'paid_amount']
        
    # Define the fields 'required'
    paid_amount = forms.DecimalField(required=True, widget=forms.TextInput(attrs={'placeholder': 'Ex.: 5.000,00', 'autocomplete': 'off', 'class': 'money-mask'}))
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