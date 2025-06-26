from datetime import datetime
import re
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
import pdfplumber
from debits.forms import LotDebitsForm, LotForm, SalesContractForm
from debits.models import Enterprise, Lot, SalesContract
from financials.models import AccountHolder, FinancialCategory, FinancialTransaction, FinancialTransactionInstallment

# Function do help extract data of debit statement
def extract_debits(pdf_path):

    debits = []
    municipal_registration = None
    statement_date = None

    # PDF Pumbler to open PDF and extract data
    with pdfplumber.open(pdf_path) as pdf:

        # for in pages
        for page in pdf.pages:

            # extract text
            text = page.extract_text()

            # lines
            lines = text.split('\n')

            # Search municipal registration only in the first page
            if not municipal_registration:
                for line in lines:
                    if 'Inscrição Imóvel:' in line:

                        # Match of municipal_registration and statement_date
                        match = re.search(r'Inscrição Imóvel:\s+(\d+)\s+(\d{2}/\d{2}/\d{4})\s+(\d{2}:\d{2}:\d{2})', line)
                        if match:
                            municipal_registration = match.group(1)
                            statement_date = datetime.strptime(f"{match.group(2)} {match.group(3)}", "%d/%m/%Y %H:%M:%S")
                        break
        
        
            # for in lines
            for line in lines:
                # Ex.: 2024 PARC IMOB FINANCIADO ... 179,84 AJUIZADO.
                match = re.match(r'(\d{4})\s+(.*?)\s+[\d\s]+(\d{2}/\d{2}/\d{4})\s+([\d.,]+)\s+([\d.,]+)\s+([\d.,]+)\s+([\d.,]+)\s+(.*)', line)
                
                # extract useful data
                if match:
                    year = int(match.group(1))
                    debit = match.group(2).strip()
                    due_date = datetime.strptime(match.group(3), '%d/%m/%Y').date()
                    amount = float(match.group(7).replace('.', '').replace(',', '.'))
                    description = match.group(8).strip().replace('.', '')
                    debits.append({
                        'year': year,
                        'debit': debit,
                        'amount': amount,
                        'due_date': due_date,
                        'description': description.upper() if description else None,
                        'statement_date': statement_date,
                        'municipal_registration': municipal_registration,

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
    fields = ['name', 'city', 'state', 'property_registration']
    template_name = 'enterprise/form.html'
    success_url = reverse_lazy('enterprise_list')

    def form_valid(self, form):

        form.instance.created_by_user = self.request.user
        form.instance.updated_by_user = self.request.user
        messages.success(self.request, 'Operação realizada com sucesso')
        return super().form_valid(form)
    
class EnterpriseUpdateView(LoginRequiredMixin, UpdateView):
    model = Enterprise
    fields = ['name', 'city', 'state', 'property_registration']
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
    paginate_by = 100

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
    
# List installments debits of IPTU
class LotInstallmentsListView(LoginRequiredMixin, ListView):
    model = FinancialTransactionInstallment
    template_name = 'lot/list_installments.html'
    
    def get_queryset(self):
        return FinancialTransactionInstallment.objects.filter(financial_transaction__lot = self.kwargs['pk'])

    
# List of updated Municipal Registration statements
class LotUpdateStatementListView(LoginRequiredMixin, ListView):
    model = Lot
    template_name = 'lot/debits.html'

# Update Municipal Registration statements
class LotUpdateStatementCreateView(LoginRequiredMixin, FormView):
    template_name = 'lot/debits_form.html'
    form_class = LotDebitsForm
    success_url = reverse_lazy('lot_debits_list')

    def form_valid(self, form):

        # files
        debit_statement_file = form.cleaned_data["files"]

        # for in files
        for file in debit_statement_file:

            # debits
            debits = extract_debits(file)

            for d in debits:
                
                # retrieve Lot
                lot = Lot.objects.filter(municipal_registration=d['municipal_registration']).first()

                # exists Lot
                if lot:
                    
                    transaction_type = None
                    sales_contract = SalesContract.objects.filter(lot=lot, is_active=1).first()
                    account_holder = get_object_or_404(AccountHolder, id=1) # TODO: company

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

class SalesContractCreateView(LoginRequiredMixin, CreateView):
    model = SalesContract
    template_name = 'sales_contract/form.html'
    form_class = SalesContractForm

    def form_valid(self, form):

        # user to save
        form.instance.created_by_user = self.request.user
        form.instance.updated_by_user = self.request.user
        form.instance.lot = get_object_or_404(Lot, id=self.kwargs.get('lot_pk')) 

        messages.success(self.request, 'Operação realizada com sucesso')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('lot_list', kwargs={'enterprise_pk': self.kwargs.get('enterprise_pk')})