
from debits.models import Lot, SalesContract
from financials.forms import BaseForm
from django import forms


# ----------
# LOT
# ----------------------

class LotForm(BaseForm):

    class Meta:
        model = Lot
        fields = ['lot', 'block', 'square_meters', 'value', 'address', 'property_registration', 'municipal_registration', 'front_footage', 'bottom_footage', 'right_footage', 'left_footage', 'corner_footage', 'front_confrontation', 'bottom_confrontation', 'right_confrontation', 'left_confrontation']


# Upload multiple files input
class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

# Upload multiple files field
class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = [single_file_clean(data, initial)]
        return result

# Upload multiple files form
class LotDebitsForm(forms.Form):
    files = MultipleFileField(label='Extratos da Inscrição Municipal')

# ----------
# SALES CONTRACT
# ----------------------

class SalesContractForm(BaseForm):

    class Meta:
        model = SalesContract
        fields = ['contract_date', 'customer_supplier', 'start_date', 'number_of_installment', 'installment_value']
        widgets = {
            'contract_date': forms.DateInput(attrs={'type': 'date'}),
            'start_date': forms.DateInput(attrs={'type': 'date'}),
        }

class SalesContractUpdateForm(BaseForm):

    class Meta:
        model = SalesContract
        fields = ['customer_supplier']

