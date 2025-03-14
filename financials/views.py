from datetime import datetime
from pyexpat.errors import messages
from django.urls import reverse_lazy
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView
from financials.filters import FinancialTransactionInstallmentFilter
from financials.forms import FinancialTransactionForm
from . import models
from django.contrib.auth.mixins import LoginRequiredMixin
from dateutil.relativedelta import relativedelta

# -----------------
# FINANCIAL TRANSACTIONS
# ----------------------------

class FinancialTransactionInstallmentListView(LoginRequiredMixin, ListView):
    model = models.FinancialTransactionInstallment
    template_name = 'financial_transaction/list.html'

    def get_queryset(self):
     
        queryset = models.FinancialTransactionInstallment.objects.all()
        
        # Cria o filtro usando os parâmetros da requisição GET
        self.filter = FinancialTransactionInstallmentFilter(self.request.GET, queryset=queryset)
        
        # Retorna o queryset filtrado
        return self.filter.qs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["filter"] = self.filter  # filter for template
        return context


class FinancialMovementCreateView(LoginRequiredMixin, CreateView):
    model = models.FinancialTransaction
    form_class = FinancialTransactionForm
    template_name = 'financial_transaction/form.html'
    success_url = reverse_lazy('dashboard')

    def form_valid(self, form):

        # add atributes to object
        form.instance.created_by_user_id = self.request.user.id
        form.instance.updated_by_user_id = self.request.user.id

        # save form object
        response = super().form_valid(form)

        # object Transaction
        transaction = self.object
        
        number_of_installments = int(self.request.POST.get('number_of_installments'))
        due_date = self.request.POST.get('due_date')

        # converting to datetime object
        due_date = datetime.strptime(due_date, "%Y-%m-%d").date() 

        # checking if the number of installments is bigger than 1
        if number_of_installments > 1:

            # save installments
            for i in range(1, number_of_installments + 1):

                # incrementing month in due date
                if i > 1:
                    due_date += relativedelta(months=1)

                models.FinancialTransactionInstallment.objects.create(
                    financial_transaction = transaction,
                    installment_number = i,
                    amount = self.request.POST.get('installment_value'),
                    due_date = due_date,
                    status = 0,
                    created_by_user_id = self.request.user.id,
                    updated_by_user_id = self.request.user.id,
                )

        return response 


    def form_invalid(self, form):
        messages.error(self.request, "Erro ao preencher o formulário. Verifique os campos.")
        return super().form_invalid(form)
    


class FinancialMovementListView(LoginRequiredMixin, ListView):
    model = models.FinancialMovement
    template_name = 'financial_movement/list.html'