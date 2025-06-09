
from debits.models import Lot
from financials.forms import BaseForm


# ----------
# LOT
# ----------------------

class LotForm(BaseForm):

    class Meta:
        model = Lot
        fields = ['lot', 'block', 'square_meters', 'value', 'address', 'property_registration', 'municipal_registration', 'front_footage', 'bottom_footage', 'right_footage', 'left_footage', 'corner_footage', 'front_confrontation', 'bottom_confrontation', 'right_confrontation', 'left_confrontation']
