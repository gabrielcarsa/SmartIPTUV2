from datetime import datetime
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView
from financials.filters import FinancialTransactionInstallmentFilter
from financials.forms import AccountHolderForm, CheckingAccountForm, TransactionForm, TransactionInstallmentAmountForm, TransactionInstallmentSettlementFormSet
from . import models
from django.contrib.auth.mixins import LoginRequiredMixin
from dateutil.relativedelta import relativedelta
from django.db.models import Sum

# ----------------------
# FINANCIAL TRANSACTION INSTALLMENTS
# -----------------------------------

# List View Transaction Installment
class TransactionInstallmentListView(LoginRequiredMixin, ListView):
    model = models.FinancialTransactionInstallment
    template_name = 'financial_transaction/list.html'
    paginate_by = 10

    def get_queryset(self):
        
        queryset = models.FinancialTransactionInstallment.objects.order_by('due_date')
        
        # create the filter using parameters from GET
        self.filter = FinancialTransactionInstallmentFilter(self.request.GET, queryset=queryset)
        
        # return queryset filter
        return self.filter.qs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["filter"] = self.filter  # filter for template
        context["querystring"] = self.request.GET.copy()

        return context

# Update installment
class TransactionInstallmentUpdateView(LoginRequiredMixin, View):
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
class TransactionInstallmentBulkSettlementView(LoginRequiredMixin, View):
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

        # checking status installment
        for installment in queryset:
            if installment.status == 1:
                messages.error(request, 'Selecione somente parcelas em aberto para baixa!')
                return redirect(request.META.get('HTTP_REFERER', 'dashboard'))

        
        formset = TransactionInstallmentSettlementFormSet(queryset=queryset)

        # context to template
        account_holders = models.AccountHolder.objects.all()
        checking_accounts = models.CheckingAccount.objects.all()

        return render(request, self.template_name, {"formset": formset, "account_holders": account_holders, "checking_accounts": checking_accounts})

    def post(self, request):

        checking_account_id = request.POST.get('checking_account');
        account_holder_id = request.POST.get('account_holder');

        # verify if both are not empty
        if not checking_account_id or  not checking_account_id:
            messages.error(request, 'Preenchar o titular e a conta corrente!')
            return redirect(request.META.get('HTTP_REFERER', 'dashboard'))
        
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

                checking_account = get_object_or_404(models.CheckingAccount, id=checking_account_id)
                
                # create Financial Movements
                models.FinancialMovement.objects.create(
                    checking_account = checking_account,
                    financial_transaction_installment = instance,
                    type = instance.financial_transaction.type,
                    amount = instance.paid_amount,
                    movement_date = instance.payment_date,
                    created_by_user = self.request.user,
                    updated_by_user = self.request.user,

                )
            
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
# FINANCIAL TRANSACTIONS
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

                # TODO down_payment

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
    

# ----------
# FINANCIAL MOVEMENTS
# ----------------------

class MovementListView(LoginRequiredMixin, ListView):
    model = models.FinancialMovement
    template_name = 'financial_movement/list.html'


# --------
# ACCOUNT HOLDERS
# ----------------

# List
class AccountHolderListView(LoginRequiredMixin, ListView):
    model = models.AccountHolder
    template_name = 'account_holder/list.html'

# Create
class AccountHolderCreateView(LoginRequiredMixin, CreateView):
    model = models.AccountHolder
    template_name = 'account_holder/form.html'
    form_class = AccountHolderForm
    success_url = reverse_lazy('account_holder_list')

    def form_valid(self, form):

        # add atributes to object
        form.instance.created_by_user_id = self.request.user.id
        form.instance.updated_by_user_id = self.request.user.id

        messages.success(self.request, "Cadastro realizado com sucesso")

        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, "Erro ao preencher o formulário. Verifique os campos.")
        return super().form_invalid(form)
    
# ---------
# CHECKING ACCOUNT
# -----------------

# List
class CheckingAccountListView(LoginRequiredMixin, ListView):
    model = models.CheckingAccount
    template_name = 'checking_account/list.html'

    def get_queryset(self):
        return super().get_queryset().filter(account_holder_id = self.kwargs.get("account_holder_id"))
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Account Holder
        account_holder = get_object_or_404(models.AccountHolder, id=self.kwargs.get("account_holder_id"))
        context['account_holder'] = account_holder
        return context

# Create
class CheckingAccountCreateView(LoginRequiredMixin, CreateView):
    model = models.CheckingAccount
    template_name = 'checking_account/form.html'
    form_class = CheckingAccountForm

    def form_valid(self, form):

        # Account Holder
        account_holder_id = self.kwargs.get('account_holder_id')
        account_holder = get_object_or_404(models.AccountHolder, id=account_holder_id)

        form.instance.account_holder = account_holder
        form.instance.created_by_user = self.request.user
        form.instance.updated_by_user = self.request.user

        messages.success(self.request, "Cadastrado com sucesso")

        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('checking_account_list', kwargs={'account_holder_id': self.kwargs.get('account_holder_id')})


    