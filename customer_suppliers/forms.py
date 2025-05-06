from django import forms
from customer_suppliers.models import CustomerSupplier
from financials.forms import BaseForm

class CustomRadioSelect(forms.RadioSelect):
    option_template_name = 'widgets/custom_radio_option.html'

class CustomerSupplierForm(BaseForm):
    class Meta:
        model = CustomerSupplier
        fields = ['type', 'name', 'email', 'phone', 'cpf', 'cnpj', 'zip_code', 'street', 'neighborhood', 'city', 'state', 'number', 'complement']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Ex.: Gabriel Henrique', 'autocomplete': 'off'}),
            'cpf': forms.TextInput(attrs={'placeholder': 'Digite CPF, caso loja for pessoa física', 'autocomplete': 'off'}),
            'cnpj': forms.TextInput(attrs={'placeholder': 'Digite CNPJ, caso loja for pessoa jurídica', 'autocomplete': 'off'}),
            'street': forms.TextInput(attrs={'readonly': 'readonly', 'class': 'bg-body-foomy', 'placeholder': 'Preencha o CEP'}),
            'neighborhood': forms.TextInput(attrs={'readonly': 'readonly', 'class': 'bg-body-foomy', 'placeholder': 'Preencha o CEP'}),
            'city': forms.TextInput(attrs={'readonly': 'readonly', 'class': 'bg-body-foomy', 'placeholder': 'Preencha o CEP'}),
            'state': forms.TextInput(attrs={'readonly': 'readonly', 'class': 'bg-body-foomy', 'placeholder': 'Preencha o CEP'}),
        }

    type = forms.ChoiceField(
        label="Tipo de cadastro",
        choices=CustomerSupplier.Type.choices,
        widget=CustomRadioSelect(attrs={'required': 'required'}),
        initial="BOTH"
    )
    
    def clean_phone(self):
        return BaseForm.clean_phone(self, 'phone')
    
    def clean_cpf(self):
        return self.clean_cpf_cnpj('cpf', 11, "CPF deve ter 11 dígitos.")

    def clean_cnpj(self):
        return self.clean_cpf_cnpj('cnpj', 14, "CNPJ deve ter 14 dígitos.")

    def clean(self):
        cleaned_data = super().clean()

        cnpj = cleaned_data.get('cnpj')
        cpf = cleaned_data.get('cpf')
        email = cleaned_data.get('email')
        phone = cleaned_data.get('phone')

        # If both fields are empty or both are filled, raise validation error
        if not cnpj and not cpf:
            self.add_error('cnpj', "Preencha pelo menos um dos campos: CNPJ ou CPF.")
            self.add_error('cpf', "Preencha pelo menos um dos campos: CNPJ ou CPF.")
            raise forms.ValidationError("Preencha pelo menos um dos campos: CNPJ ou CPF.")

        if cnpj and cpf:
            self.add_error('cnpj', "Preencha apenas um dos campos: CNPJ ou CPF. Não ambos.")
            self.add_error('cpf', "Preencha apenas um dos campos: CNPJ ou CPF. Não ambos.")
            raise forms.ValidationError("Preencha apenas um dos campos: CNPJ ou CPF. Não ambos.")

        return cleaned_data