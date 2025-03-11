from django.views.generic.list import ListView
from financials.models import FinancialMovement

class FinancialMovementListView(ListView):
    model = FinancialMovement
    template_name = 'financial_movement/list.html'