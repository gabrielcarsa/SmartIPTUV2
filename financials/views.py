from datetime import datetime
from django.contrib import messages
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView
from financials.filters import FinancialTransactionInstallmentFilter
from financials.forms import TransactionForm, TransactionInstallmentAmountForm, TransactionInstallmentSettlementFormSet
from . import models
from django.contrib.auth.mixins import LoginRequiredMixin
from dateutil.relativedelta import relativedelta

# ----------------------
# FINANCIAL TRANSACTION INSTALLMENTS
# -----------------------------------

# List View Transaction Installment
class TransactionInstallmentListView(LoginRequiredMixin, ListView):
    model = models.FinancialTransactionInstallment
    template_name = 'financial_transaction/list.html'

    def get_queryset(self):
     
        queryset = models.FinancialTransactionInstallment.objects.all().order_by('due_date')
        
        # create the filter using parameters from GET
        self.filter = FinancialTransactionInstallmentFilter(self.request.GET, queryset=queryset)
        
        # return queryset filter
        return self.filter.qs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["filter"] = self.filter  # filter for template
        return context

# Update installment
class TransactionInstallmentsUpdateView(LoginRequiredMixin, View):
    model = models.FinancialTransactionInstallment
    template_name = "financial_transaction/update_form.html"

    def get(self, request):
        ids = request.GET.get("checkboxes")
        if not ids:
            messages.error(request, 'Nenhuma parcela selecionada!')
            return redirect(request.META.get('HTTP_REFERER', 'dashboard'))

        form = TransactionInstallmentAmountForm()
        format_ids = ids.split(",")

        installments = models.FinancialTransactionInstallment.objects.filter(id__in=format_ids)

        return render(request, self.template_name, {"form": form, "ids": ids, "installments": installments})

    def post(self, request):
        form = TransactionInstallmentAmountForm(request.POST)
        ids = request.POST.get("ids", "").split(",")

        if form.is_valid():
            amount = form.cleaned_data["amount"]

            # update all selected registers
            models.FinancialTransactionInstallment.objects.filter(id__in=ids).update(amount=amount)

            messages.success(request, "Parcelas atualizadas com sucesso!")
            return redirect("financial_transaction_list")

        return render(request, self.template_name, {"form": form})


# Settlement installment
class TransactionInstallmentsBulkSettlementView(LoginRequiredMixin, View):
    template_name = "financial_transaction/settlement_form.html"

    def get(self, request):
        # get selected checkboxes IDs
        ids = request.GET.get("checkboxes")

        # checking IDs
        if not ids:
            messages.error(request, 'Nenhuma parcela selecionada!')
            return redirect(request.META.get('HTTP_REFERER', 'dashboard'))

        # split into array 
        ids = ids.split(",")

        queryset = models.FinancialTransactionInstallment.objects.filter(id__in=ids)
        formset = TransactionInstallmentSettlementFormSet(queryset=queryset)

        # context to template
        account_holders = models.AccountHolder.objects.all()
        checking_accounts = models.CheckingAccount.objects.all()

        return render(request, self.template_name, {"formset": formset, "account_holders": account_holders, "checking_accounts": checking_accounts})

    def post(self, request):
        # formset
        formset = TransactionInstallmentSettlementFormSet(request.POST)

        # valid form
        if formset.is_valid():

            # get object without save
            instances = formset.save(commit=False)

            # update fields
            for instance in instances:
                instance.status = 1
                instance.settlement_date = datetime.now()
                instance.marked_down_by_user = self.request.user
                instance.save()
            
            return redirect("financial_transaction_list")
        
        # invalid form, show errors
        if not formset.is_valid():
            for form in formset:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"{field}: {error}")
            for error in formset.non_form_errors():
                messages.error(request, error)

        return render(request, self.template_name, {"formset": formset})



# ----------
# FINANCIAL TRANSACTION
# ----------------------

# Create Transaction
class TransactionCreateView(LoginRequiredMixin, CreateView):
    model = models.FinancialTransaction
    form_class = TransactionForm
    template_name = 'financial_transaction/form.html'
    success_url = reverse_lazy('financial_transaction_list')

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
    


class MovementListView(LoginRequiredMixin, ListView):
    model = models.FinancialMovement
    template_name = 'financial_movement/list.html'