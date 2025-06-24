from datetime import datetime
from decimal import Decimal
import json
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, FormView
from ofxparse import OfxParser
from financials.filters import FinancialMovementFilter, FinancialTransactionInstallmentFilter
from financials.forms import AccountHolderForm, CheckingAccountForm, FinancialCategoryForm, MovimentsFormSet, OFXUploadForm, TransactionForm, TransactionInstallmentAmountForm, TransactionInstallmentDueDateForm, TransactionInstallmentSettlementFormSet
from . import models
from django.contrib.auth.mixins import LoginRequiredMixin
from dateutil.relativedelta import relativedelta
from django.utils import timezone
from django.db.models import F
from django.template.loader import render_to_string
from weasyprint import HTML

# ----------------
# CHECKING ACCOUNT BALANCES
# --------------------------

class CheckingAccountBalanceView(View):

    # update or create balance
    def update_or_create(self, date, amount, checking_account_id, type):
        
        # get Checking Account
        checking_account = get_object_or_404(models.CheckingAccount, id=checking_account_id)

        # get previous balance
        previous_balance = models.CheckingAccountBalance.objects.filter(
            balance_date__lte=date,
            checking_account=checking_account,
        ).order_by('-balance_date').first()

        # value previous balance
        value_previous_balance = 0

        # verify Previous Balance exists, and define value
        if previous_balance:
            value_previous_balance = previous_balance.balance
        else:
            value_previous_balance = checking_account.initial_balance

        # create or update Balance
        obj, created = models.CheckingAccountBalance.objects.update_or_create(
            balance_date=date,
            checking_account=checking_account,
            defaults={
                "checking_account": checking_account,
                "balance": value_previous_balance - amount if type == 0 else value_previous_balance + amount,
            },
            create_defaults={
                "balance_date": date,
                "checking_account": checking_account,
                "balance": value_previous_balance - amount if type == 0 else value_previous_balance + amount,
            },
        )


        # updates all future balances
        adjustment = -amount if type == 0 else amount

        models.CheckingAccountBalance.objects.filter(
            checking_account=checking_account,
            balance_date__gt=date,  # later dates only
        ).update(
            balance=F('balance') + adjustment
        )

        return obj
    
# List
class CheckingAccountBalanceListView(ListView):
    model = models.CheckingAccountBalance
    template_name = 'checking_account_balance/list.html'

    def get_queryset(self):
        return super().get_queryset().filter(checking_account=self.kwargs.get('account_holder_id'))
    
    def get_context_data(self, **kwargs):
        
        context = super().get_context_data(**kwargs)

        # retrieve account balances
        balances = models.CheckingAccountBalance.objects.filter(checking_account=self.kwargs.get('account_holder_id'))

        if balances: 

            array_dates = []
            array_balances = []

            for balance in balances:
                array_dates.append(balance.balance_date.strftime('%d/%m/%Y')) 
                array_balances.append(float(balance.balance)) 

            context['array_dates'] = array_dates
            context['array_balances'] = array_balances

        # checking account
        context['checking_account'] = get_object_or_404(models.CheckingAccount, id=self.kwargs.get('account_holder_id'))

        return context


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

        # Installments IDs
        ids = request.GET.get("checkboxes")

        # check that there are no selected installments
        if not ids:
            messages.error(request, 'Nenhuma parcela selecionada!')
            return redirect(request.META.get('HTTP_REFERER', 'dashboard'))
        
        # split ','
        format_ids = ids.split(",")

        # get installments
        installments = models.FinancialTransactionInstallment.objects.filter(id__in=format_ids)

        # define update operation
        if request.GET.get("operation") == 'amount':
            form = TransactionInstallmentAmountForm()
        elif request.GET.get("operation") == 'due_date':
            form = TransactionInstallmentDueDateForm()
        elif request.GET.get("operation") == 'reverse_payment':
            form = None
        elif request.GET.get("operation") == 'delete':
            form = None

            # search paid installments
            paid_installments = models.FinancialTransactionInstallment.objects.filter(id__in=format_ids,status=1)

            # redirect back if has paid installments
            if paid_installments:
                messages.error(request, 'Selecione apenas parcelas em aberto ou estorne o pagamento/recebimento das parcelas pagas para continuar!')
                return redirect(request.META.get('HTTP_REFERER', 'dashboard'))
        
        return render(
            request, 
            self.template_name, 
            {
                "form": form, 
                "ids": ids, 
                "installments": installments
            }
        )

    def post(self, request):

        # Installments IDs
        ids = request.POST.get("ids", "").split(",")

        # type of update
        operation = request.POST.get("operation")

        # assign the correct form to the operation
        if operation == 'amount':
            form = TransactionInstallmentAmountForm(request.POST)     

        elif operation == 'due_date':
            form = TransactionInstallmentDueDateForm(request.POST)  

        elif operation == 'reverse_payment':

            installments = models.FinancialTransactionInstallment.objects.filter(id__in=ids)
            movements = models.FinancialMovement.objects.filter(financial_transaction_installment__in=ids)
            
            # for in movements to balances update 
            for movement in movements:

                balances = models.CheckingAccountBalance.objects.filter(
                    balance_date__gte=movement.movement_date
                )

                # update balances
                for balance in balances:

                    if movement.type == 0:
                        balance.balance += movement.amount
                        balance.save()
                    else: 
                        balance.balance -= movement.amount
                        balance.save()
                        
            
            # delete movements
            movements.delete()
                
            # reverse payments data
            installments.update(
                payment_date=None, 
                status=0, 
                paid_amount=None, 
                settlement_date= None, 
                marked_down_by_user=None
            )

            messages.success(request, "Operação realizada com sucesso!")
            return redirect("financial_transaction_list")     

        elif operation == 'delete':

            installments = models.FinancialTransactionInstallment.objects.filter(id__in=ids).delete()

            messages.success(request, "Operação realizada com sucesso!")
            return redirect("financial_transaction_list")  
            
        if form.is_valid():

            # update amount
            if operation == 'amount':

                amount = form.cleaned_data["amount"]

                # update all selected registers
                models.FinancialTransactionInstallment.objects.filter(id__in=ids).update(amount=amount)

            # update due_date
            elif operation == 'due_date':

                due_date = form.cleaned_data["due_date"]

                # get all selected registers
                installments = models.FinancialTransactionInstallment.objects.filter(id__in=ids)
            
                # update all selected
                for i, installment in enumerate(installments):
                    installment.due_date = due_date + relativedelta(months=i)
                    installment.save()

                
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

                # not allowed settlement in previous date
                if instance.payment_date > timezone.now():
                    messages.error(request, 'Não é possível dar baixar em datas futuras!')
                    return redirect(request.META.get('HTTP_REFERER', 'dashboard'))
                

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
                    description = instance.financial_transaction.description,
                    movement_date = instance.payment_date,
                    created_by_user = self.request.user,
                    updated_by_user = self.request.user,

                )

                # CheckingAccountBalanceView instance for balance management
                checking_account_balance_class = CheckingAccountBalanceView()

                # call function to create or update balance
                checking_account_balance_class.update_or_create(
                    date = instance.payment_date,
                    amount = instance.paid_amount,
                    checking_account_id = checking_account.id,
                    type = instance.financial_transaction.type,
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
        installment_value = self.request.POST.get('installment_value')
        down_payment = str(self.request.POST.get('down_payment')).replace('.', '').replace(',', '.')

        # converting to datetime object
        due_date = datetime.strptime(due_date, "%Y-%m-%d").date() 

        # save installments
        for i in range(1, number_of_installments + 1):

            # auxiliary variable to store the amount
            installment_value_aux = 0

            # define installment amount
            if down_payment and i == 1:
                installment_value_aux = down_payment
            else:
                installment_value_aux = str(installment_value).replace('.', '').replace(',', '.')

            # incrementing month in due date
            if i > 1:
                due_date += relativedelta(months=1)

            models.FinancialTransactionInstallment.objects.create(
                financial_transaction = transaction,
                installment_number = i,
                amount = installment_value_aux,
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
    paginate_by = 30

    def get_queryset(self):

        queryset = models.FinancialMovement.objects.order_by('movement_date', 'order')     

        # create the filter using parameters from GET
        self.filter = FinancialMovementFilter(self.request.GET, queryset=queryset)

        # check if any filters have been applied
        if not any(self.request.GET.values()):
            queryset.none()
        
        # return queryset filter
        return self.filter.qs

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        if any(self.request.GET.values()):

            account_id = self.request.GET.get('checking_account')
            start_date = self.request.GET.get('movement_date__gte')
            end_date = self.request.GET.get('movement_date__lte')

            context['start_date'] = start_date
            context['end_date'] = end_date
            context['account_id'] = account_id

            # retrieve previous balance
            context['previous_balance'] = models.CheckingAccountBalance.objects.filter(
                balance_date__lt = start_date,
                checking_account = account_id,
            ).order_by('balance_date').last()

            # retrieve current balance
            context['balance'] = models.CheckingAccountBalance.objects.filter(
                balance_date__lte = end_date,
                checking_account = account_id,
            ).order_by('balance_date').last()

       
        context["filter"] = self.filter  # filter for template
        context["querystring"] = self.request.GET.copy()
    

        return context
    
class MovementListPDF(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):

        account_id = request.GET.get('checking_account')
        start_date = request.GET.get('movement_date__gte')
        end_date = request.GET.get('movement_date__lte')

        # retrieve previous balance
        previous_balance = models.CheckingAccountBalance.objects.filter(
            balance_date__lt = start_date,
            checking_account = account_id,
        ).order_by('balance_date').last()

        # retrieve current balance
        balance = models.CheckingAccountBalance.objects.filter(
            balance_date__lte = end_date,
            checking_account = account_id,
        ).order_by('balance_date').last()

        financialmovement_list = models.FinancialMovement.objects.filter(
            movement_date__gte = start_date,
            movement_date__lte = end_date,
            checking_account = account_id,
        ).order_by('movement_date', 'order')     

        html_string = render_to_string("financial_movement/report.html", 
            {
                "previous_balance": previous_balance, 
                "balance": balance,
                "account_id": account_id,
                "start_date": start_date,
                "end_date": end_date,
                "financialmovement_list": financialmovement_list,
            }
        )

        pdf_file = HTML(string=html_string).write_pdf()

        response = HttpResponse(pdf_file, content_type="application/pdf")
        response['Content-Disposition'] = 'filename="relatorio.pdf"'

        return response
    
# Change order
class MovementUpdateOrderView(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):

        id = self.request.GET.get('id')
        order = self.request.GET.get('order')

        movement = models.FinancialMovement.objects.get(id=id)
        movement.order = order
        movement.save()

        return redirect(request.META.get('HTTP_REFERER', 'dashboard'))
    
# Upload OFX file 
class MovementImportOFXView(LoginRequiredMixin, FormView):
    template_name = 'financial_movement/ofx_upload.html'
    form_class = OFXUploadForm

    def form_valid(self, form):

        # catch file
        ofx_file = form.cleaned_data['file']
        ofx = OfxParser.parse(ofx_file)

        # array initial data
        initial_data = []

        # for in transactions
        for transaction in ofx.account.statement.transactions:

            # add on array transactions data
            initial_data.append({
                'movement_date': transaction.date,
                'amount': Decimal(abs(transaction.amount)),
                'description': transaction.memo,
                'type': 1 if transaction.amount > 0 else 0,
            })

        # define formset
        formset = MovimentsFormSet(initial=initial_data)

        # render html to review before save
        return render(self.request, 'financial_movement/ofx_review.html', {
            'formset': formset,
            'account_holders': models.AccountHolder.objects.all(),
            'checking_accounts': models.CheckingAccount.objects.all(),
        })
    
# Save Movements of OFX file
class MovementImportSaveView(LoginRequiredMixin, View):

    def post(self, request):
        
        # formset
        formset = MovimentsFormSet(request.POST)

        if formset.is_valid():
            
            # count of Movemets saves
            count = 0

            checking_account = get_object_or_404(models.CheckingAccount, id=request.POST.get('checking_account'))
            account_holder = get_object_or_404(models.AccountHolder, id=request.POST.get('account_holder'))

            for form in formset:

                # ignore forms marked by Delete
                if form.cleaned_data.get('DELETE'):
                    continue

                # clean data of form
                data = form.cleaned_data

                # verify if Movement alredy exists
                if not models.FinancialMovement.objects.filter(
                    movement_date=data['movement_date'],
                    amount=data['amount'],
                    description=data['description']
                ).exists():

                
                    if not data['transaction_installment']:

                        # create Transaction
                        transaction = models.FinancialTransaction.objects.create(
                            type=data['type'],
                            description=data['description'],
                            installment_value=data['amount'],
                            due_date=data['movement_date'],
                            number_of_installments=1,
                            account_holder=account_holder,
                            financial_category=data['category'],
                            customer_supplier=data['customer_supplier'],
                            created_by_user=request.user,
                            updated_by_user=request.user,
                        )
                    else:
                        transaction = data['transaction_installment'].financial_transaction 

                    # update or create Installment
                    obj, created = models.FinancialTransactionInstallment.objects.update_or_create(
                        id=data['transaction_installment'].id if data['transaction_installment'] else None,
                        defaults={
                            "payment_date":data['movement_date'],
                            "status":1,
                            "paid_amount":data['amount'],
                            "settlement_date":datetime.now(),
                            "updated_by_user":request.user,
                            "marked_down_by_user":request.user,
                        },
                        create_defaults = {
                            "financial_transaction": transaction,
                            "installment_number": 1,
                            "amount": data['amount'],
                            "due_date": data['movement_date'],
                            "created_by_user": request.user,
                            "payment_date":data['movement_date'],
                            "status":1,
                            "paid_amount":data['amount'],
                            "settlement_date":datetime.now(),
                            "updated_by_user":request.user,
                            "marked_down_by_user":request.user,
                        },
                    )

                    # create Movement
                    models.FinancialMovement.objects.create(
                        financial_transaction_installment=obj,
                        movement_date=data['movement_date'],
                        amount=data['amount'],
                        description=data['description'],
                        type=data['type'],
                        checking_account=checking_account,
                        created_by_user=request.user,
                        updated_by_user=request.user,
                    )

                    # CheckingAccountBalanceView instance for balance management
                    checking_account_balance_class = CheckingAccountBalanceView()

                    # call function to create or update balance
                    checking_account_balance_class.update_or_create(
                        date = data['movement_date'],
                        amount = data['amount'],
                        checking_account_id = checking_account.id,
                        type = data['type'],
                    )
                    count += 1

            messages.success(request, f"{count} movimentações salvas com sucesso.")
            return redirect('financial_movements_list')
        else:
            return render(request, 'financial_movement/ofx_review.html', {
                'formset': formset,
                'account_holders': models.AccountHolder.objects.all(),
                'checking_accounts': models.CheckingAccount.objects.all(),
            })

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
        return reverse_lazy('account_holder_list')


# Update
class CheckingAccountUpdateView(LoginRequiredMixin, UpdateView):
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
        return reverse_lazy('account_holder_list')

# ----------
# FINANCIAL CATEGORY
# ------------------

# List
class FinancialCategoryListView(LoginRequiredMixin, ListView):
    model = models.FinancialCategory
    template_name = 'financial_category/list.html'


# Create
class FinancialCategoryCreateView(LoginRequiredMixin, CreateView):
    model = models.FinancialCategory
    template_name = 'financial_category/form.html'
    form_class = FinancialCategoryForm

    def form_valid(self, form):

        form.instance.created_by_user = self.request.user
        form.instance.updated_by_user = self.request.user

        messages.success(self.request, "Cadastrado com sucesso")

        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('financial_category_list')
    
# Update
class FinancialCategoryUpdateView(LoginRequiredMixin, UpdateView):
    model = models.FinancialCategory
    template_name = 'financial_category/form.html'
    form_class = FinancialCategoryForm

    def form_valid(self, form):

        form.instance.updated_by_user = self.request.user
        messages.success(self.request, "Atualizado com sucesso")

        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('financial_category_list')

