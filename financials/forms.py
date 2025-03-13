import re
from django import forms

from financials.models import FinancialTransaction

# Helper function to clean numbers (remove non-digit characters)
def clean_number(value):
    return re.sub(r'\D', '', value or '')

# Base class for form validation (boostrap, clean masks)
class BaseForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(BaseForm, self).__init__(*args, **kwargs)

        # Define class bootstrap for all fields 
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})
        
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
    

class FinancialTransactionForm(BaseForm):

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
        
