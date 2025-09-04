from datetime import datetime
import re
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
import pdfplumber
from debits.forms import LotDebitsForm, LotForm, SalesContractForm, SalesContractUpdateForm
from debits.models import Enterprise, Lot, SalesContract
from financials.models import AccountHolder, FinancialCategory, FinancialTransaction, FinancialTransactionInstallment
from django.db.models import Sum
from django.db.models import OuterRef, Subquery
from django.utils import timezone

# Function do help extract data of debit statement
def extract_debits(pdf_path):

    debits = []
    municipal_registration = None
    statement_date = None
    taxpayer = None

    # PDF Pumbler to open PDF and extract data
    with pdfplumber.open(pdf_path) as pdf:

        # for in pages
        for page_num, page in enumerate(pdf.pages):

            # extract text
            text = page.extract_text()

            # lines
            lines = text.split('\n')

            # Search municipal registration only in the first page
            if page_num == 0:  # Verifica apenas na primeira página
                for line in lines:
                    if 'Inscrição Imóvel:' in line:
                        match = re.search(r'Inscrição Imóvel:\s+(\d+)\s+(\d{2}/\d{2}/\d{4})\s+(\d{2}:\d{2}:\d{2})', line)
                        if match:
                            municipal_registration = match.group(1)
                            statement_date = datetime.strptime(f"{match.group(2)} {match.group(3)}", "%d/%m/%Y %H:%M:%S")
                    if 'Contribuinte:' in line:
                        match = re.search(r'Contribuinte:\s+(.*)', line)
                        if match:
                            taxpayer = match.group(1).strip()
        
        
            # for in lines
            for line in lines:
                # Ex.: 2024 PARC IMOB FINANCIADO ... 179,84 AJUIZADO.
                match = re.match(
                    r'(\d{4})\s+(.*?)\s+[\d\s]+(\d{2}/\d{2}/\d{4})\s+([\d.,]+)\s+([\d.,]+)\s+([\d.,]+)\s+([\d.,]+)(?:\s+(.*))?$',
                    line
                )
                
                # extract useful data
                if match:
                    year = int(match.group(1))
                    debit = match.group(2).strip()
                    due_date = datetime.strptime(match.group(3), '%d/%m/%Y').date()
                    amount = float(match.group(7).replace('.', '').replace(',', '.'))
                    description = match.group(8).strip().replace('.', '') if match.group(8) else 'IPTU ANUAL'
                    debits.append({
                        'year': year,
                        'debit': debit,
                        'amount': amount,
                        'due_date': due_date,
                        'description': description.upper(),
                        'statement_date': statement_date,
                        'municipal_registration': municipal_registration,
                        'taxpayer': taxpayer,
                    })
    return debits

# ----------------------
# ENTERPRISE
# -----------------------------------

class EnterpriseListView(LoginRequiredMixin, ListView):
    model = Enterprise
    template_name = 'enterprise/list.html'
    paginate_by = 100

class EnterpriseCreateView(LoginRequiredMixin, CreateView):
    model = Enterprise
    fields = ['name', 'city', 'state', 'property_registration', 'code_erp']
    template_name = 'enterprise/form.html'
    success_url = reverse_lazy('enterprise_list')

    def form_valid(self, form):

        form.instance.created_by_user = self.request.user
        form.instance.updated_by_user = self.request.user
        messages.success(self.request, 'Operação realizada com sucesso')
        return super().form_valid(form)
    
class EnterpriseUpdateView(LoginRequiredMixin, UpdateView):
    model = Enterprise
    fields = ['name', 'city', 'state', 'property_registration', 'code_erp']
    template_name = 'enterprise/form.html'
    success_url = reverse_lazy('enterprise_list')

    def form_valid(self, form):

        form.instance.updated_by_user = self.request.user
        messages.success(self.request, 'Operação realizada com sucesso')
        return super().form_valid(form)
    
class EnterpriseDeleteView(LoginRequiredMixin, DeleteView):
    model = Enterprise
    template_name = 'enterprise/delete.html'
    success_url = reverse_lazy('enterprise_list')

    def form_valid(self, form):

        messages.success(self.request, 'Operação realizada com sucesso')
        return super().form_valid(form)
    


# ----------------------
# BLOCK
# -----------------------------------

# ----------------------
# LOT
# -----------------------------------

# List Lots
class LotListView(LoginRequiredMixin, ListView):
    model = Lot
    template_name = 'lot/list.html'

    def get_queryset(self):

        # query total debts per costumer
        costumer_total_debt = FinancialTransactionInstallment.objects.filter(
            financial_transaction__lot = OuterRef("pk"), 
            financial_transaction__type = 1,
            due_date__lte= timezone.now(),
        ).values(
            'financial_transaction__lot' # groups the results by Lot.
        ).annotate(
            total_debt=Sum('amount') # calculates the sum of the values of the installments in this Lot
        ).values('total_debt') # subquery return only the total_debt column
        
        # Lot with total debts per costumer
        return Lot.objects.filter(
            block__enterprise=self.kwargs['enterprise_pk']
        ).annotate(
            costumer_total_debt=Subquery(costumer_total_debt)
        ).order_by('block__name', 'lot')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['enterprise'] = get_object_or_404(Enterprise, id=self.kwargs['enterprise_pk'])
        return context

# Create
class LotCreateView(LoginRequiredMixin, CreateView):
    model = Lot
    template_name = 'lot/form.html'
    form_class = LotForm

    def form_valid(self, form):

        # user to save
        form.instance.created_by_user = self.request.user
        form.instance.updated_by_user = self.request.user

        messages.success(self.request, 'Operação realizada com sucesso')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('lot_list', kwargs={'enterprise_pk': self.kwargs.get('enterprise_pk')})
    
# Update
class LotUpdateView(LoginRequiredMixin, UpdateView):
    model = Lot
    template_name = 'lot/form.html'
    form_class = LotForm

    def form_valid(self, form):

        # user to save
        form.instance.updated_by_user = self.request.user
        
        messages.success(self.request, 'Operação realizada com sucesso')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('lot_list', kwargs={'enterprise_pk': self.kwargs.get('enterprise_pk')})
    
# Delete
class LotDeleteView(LoginRequiredMixin, DeleteView):
    model = Lot
    template_name = 'lot/delete.html'

    def form_valid(self, form):

        messages.success(self.request, 'Operação realizada com sucesso')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('lot_list', kwargs={'enterprise_pk': self.kwargs.get('enterprise_pk')})
    
# List the lot's iptu installments
class LotInstallmentsListView(LoginRequiredMixin, ListView):
    model = FinancialTransactionInstallment
    template_name = 'lot/list_installments.html'
    
    def get_queryset(self):
        return FinancialTransactionInstallment.objects.filter(financial_transaction__lot = self.kwargs['pk'])

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        # get Lot
        context['lot'] = get_object_or_404(Lot, id=self.kwargs['pk'])

        # total company debts
        context['company_total_debt'] = FinancialTransactionInstallment.objects.filter(
            financial_transaction__lot = self.kwargs['pk'], 
            financial_transaction__type = 0,
        ).aggregate(total=Sum('amount'))['total'] or 0

        # total costumer debts
        context['costumer_total_debt'] = FinancialTransactionInstallment.objects.filter(
            financial_transaction__lot = self.kwargs['pk'], 
            financial_transaction__type = 1,
        ).aggregate(total=Sum('amount'))['total'] or 0

        return context
    
# List of updated Municipal Registration statements
class LotUpdateStatementListView(LoginRequiredMixin, ListView):
    model = Lot
    template_name = 'lot/debits.html'

    def get_queryset(self):
        return Lot.objects.all().order_by('latest_update')

# Update Municipal Registration statements
class LotUpdateStatementCreateView(LoginRequiredMixin, FormView):
    template_name = 'lot/debits_form.html'
    form_class = LotDebitsForm
    success_url = reverse_lazy('lot_debits_list')

    def form_valid(self, form):

        # files
        debit_statement_file = form.cleaned_data["files"]

        operation_hour = timezone.now()

        # for in files
        for file in debit_statement_file:

            # debits
            debits = extract_debits(file)

            for d in debits:
                
                # retrieve Lot
                lot = Lot.objects.filter(municipal_registration=d['municipal_registration']).first()

                # exists Lot
                if lot:

                    # delete all transactions in the Lot to create news them below
                    FinancialTransaction.objects.filter(lot=lot, created_at__lt=operation_hour).delete()
                    
                    transaction_type = None
                    sales_contract = SalesContract.objects.filter(lot=lot, is_active=1).first()

                    # get the Company register
                    account_holder = AccountHolder.objects.filter(
                        customer_supplier__type_customer_supplier__name__iexact='Empresa'
                    ).first()

                    if not account_holder:
                        messages.error(self.request, 'Não encontrado Titular de Conta com cadastro de Empresa.')
                        return super().form_invalid(form)
                    
                    # check if is property deed 
                    if d['taxpayer'] != account_holder.customer_supplier.name:
                        lot.is_property_deed = True
                    else:
                        lot.is_property_deed = False

                    # update Lot
                    lot.latest_update = d['statement_date']
                    lot.save()
                    
                    # verify sales contract and date to define transaction type
                    if sales_contract:
                        if sales_contract.contract_date > d['due_date']:
                            transaction_type = 0
                        else:
                            transaction_type = 1
                    else:
                        transaction_type = 0

                    # search Financial Category
                    financial_category = FinancialCategory.objects.filter(name=d['description']).first()

                    # if not exists, create
                    if not financial_category:
                        financial_category = FinancialCategory.objects.create(
                            name=d['description'],
                            created_by_user=self.request.user,
                            updated_by_user=self.request.user,
                        )


                    # create transaction
                    transaction = FinancialTransaction.objects.create(
                        type=transaction_type,
                        lot=lot,
                        description=d['debit'],
                        installment_value=d['amount'],
                        due_date=d['due_date'],
                        number_of_installments=1,
                        account_holder=account_holder,
                        financial_category=financial_category,
                        customer_supplier=sales_contract.customer_supplier if transaction_type == 1 else account_holder.customer_supplier,
                        created_by_user=self.request.user,
                        updated_by_user=self.request.user,
                    )

                    # create installment
                    transaction_installment = FinancialTransactionInstallment.objects.create(
                        financial_transaction = transaction,
                        installment_number = 1,
                        amount = d['amount'],
                        due_date = d['due_date'],
                        created_by_user=self.request.user,
                        updated_by_user=self.request.user,
                    )


        messages.success(self.request, 'Operação realizada com sucesso')
        return super().form_valid(form)



# ----------------------
# SALES CONTRACT
# -----------------------------------

# Create
class SalesContractCreateView(LoginRequiredMixin, CreateView):
    model = SalesContract
    template_name = 'sales_contract/form.html'
    form_class = SalesContractForm

    def dispatch(self, request, *args, **kwargs):

        lot = get_object_or_404(Lot, id=self.kwargs.get('lot_pk')) 

        sales_contract = SalesContract.objects.filter(lot=lot, is_active=1).first()

        # if alredy exists active contract
        if sales_contract:
            messages.error(self.request, 'Já existe um contrato ativo para esse lote, faço primeiro o cancelamento do contrato atual!')
            return redirect('lot_list', enterprise_pk=self.kwargs.get('enterprise_pk'))

        return super().dispatch(request, *args, **kwargs)
        

    def form_valid(self, form):

        # user to save
        form.instance.created_by_user = self.request.user
        form.instance.updated_by_user = self.request.user
        form.instance.is_active = 1
        form.instance.lot = get_object_or_404(Lot, id=self.kwargs.get('lot_pk')) 

        messages.success(self.request, 'Operação realizada com sucesso')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Erro')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('lot_list', kwargs={'enterprise_pk': self.kwargs.get('enterprise_pk')})
    
# Update CustomerSupplier - assignment of rights
class SalesContractUpdateView(LoginRequiredMixin, UpdateView):
    model = SalesContract
    template_name = 'sales_contract/form.html'
    form_class = SalesContractUpdateForm

    def form_valid(self, form):

        form.instance.updated_by_user = self.request.user

        messages.success(self.request, 'Operação realizada com sucesso')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Erro')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('lot_list', kwargs={'enterprise_pk': self.kwargs.get('enterprise_pk')})
    
# Cancel
class SalesContractCancelView(LoginRequiredMixin, View):
    template_name = 'sales_contract/cancel.html'

    def get(self, request, *args, **kwargs):

        sales_contract = get_object_or_404(SalesContract, id=kwargs.get('pk'))
        sales_contract.is_active = 0
        sales_contract.save()

        messages.success(self.request, 'Contrato cancelado com sucesso')
        return redirect('lot_list', enterprise_pk=self.kwargs.get('enterprise_pk'))