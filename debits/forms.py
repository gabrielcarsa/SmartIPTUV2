
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