from datetime import datetime
import math
import re
import unicodedata
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
import pdfplumber
import pandas as pd
from customer_suppliers.models import CustomerSupplier
from debits.forms import LotDebitsForm, LotForm, SalesContractForm, SalesContractUpdateExcelForm, SalesContractUpdateForm
from debits.models import Block, Enterprise, Lot, SalesContract
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

class LotExportExcelListView(View):

    def get(self, request, *args, **kwargs):
        enterprise_pk = self.kwargs['enterprise_pk']

        costumer_total_debt = FinancialTransactionInstallment.objects.filter(
            financial_transaction__lot=OuterRef("pk"),
            financial_transaction__type=1,
            due_date__lte=timezone.now(),
        ).values(
            'financial_transaction__lot'
        ).annotate(
            total_debt=Sum('amount')
        ).values('total_debt')

        company_total_debt = FinancialTransactionInstallment.objects.filter(
            financial_transaction__lot=OuterRef("pk"),
            financial_transaction__type=0,
            due_date__lte=timezone.now(),
        ).values(
            'financial_transaction__lot'
        ).annotate(
            total_debt=Sum('amount')
        ).values('total_debt')
        
        lots = Lot.objects.filter(
            block__enterprise=enterprise_pk
        ).annotate(
            costumer_total_debt=Subquery(costumer_total_debt),
            company_total_debt=Subquery(company_total_debt)
        ).order_by('block__name', 'lot')

        data = []
        for lot in lots:
            sales_contract = SalesContract.objects.filter(lot=lot, is_active=True).first() 
            data.append({
                'Empreendimento': lot.block.enterprise.name,
                'Quadra': lot.block.name,
                'Lote': lot.lot,
                'Última atual.': lot.latest_update,
                'Cliente': sales_contract.customer_supplier.name if sales_contract else 'LOTE LIVRE',
                'Inscrição': lot.municipal_registration,
                'IPTU Empresa': lot.company_total_debt or 0,
                'IPTU Cliente ': lot.costumer_total_debt or 0,
            })

        df = pd.DataFrame(data)

        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )
        response['Content-Disposition'] = 'attachment; filename=lots.xlsx'

        with pd.ExcelWriter(response, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Lots')

        return response

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

class SalesContractUpdateExcelView(FormView):
    template_name = "sales_contract/upload_excel.html"
    form_class = SalesContractUpdateExcelForm

    def form_valid(self, form):
        file = form.cleaned_data["arquivo"]
        updates_contracts = 0
        created_contracts = 0

        try:
            df = pd.read_excel(file)

            # Colunas obrigatórias
            necessary_columns = [
                "Cliente", "Data Venda", "Quadra", "Lote", "Valor Venda",
                "Valor Entrada", "Valor Parcela Entrada", "Qtd Entrada",
                "Qtd Parcelas", "Valor Parcela Financiamento", "1º Vencimento", "Status"
            ]
            if not all(col in df.columns for col in necessary_columns):
                messages.error(self.request, f"Colunas esperadas: {necessary_columns}")
                return self.form_invalid(form)

            for _, row in df.iterrows():
                try:
                    # Dados básicos
                    customer_name = str(row["Cliente"]).strip() if pd.notna(row["Cliente"]) else ""
                    block_name = str(row["Quadra"]).strip() if pd.notna(row["Quadra"]) else ""
                    lot_name = str(row["Lote"]).strip() if pd.notna(row["Lote"]) else ""
                    status = str(row["Status"]).strip() if pd.notna(row["Status"]) else ""

                    # Datas
                    def parse_date(value):
                        if pd.isna(value):
                            return None
                        if isinstance(value, datetime):
                            return value.date()
                        for fmt in ("%Y-%m-%d", "%d/%m/%Y"):
                            try:
                                return datetime.strptime(str(value), fmt).date()
                            except ValueError:
                                continue
                        return None

                    contract_date = parse_date(row["Data Venda"])
                    start_date = parse_date(row["1º Vencimento"])

                    # Valores numéricos
                    def parse_decimal(value):
                        if pd.isna(value):
                            return None
                        try:
                            val = float(str(value).replace(",", "."))
                            if math.isnan(val):
                                return None
                            return val
                        except (ValueError, TypeError):
                            return None

                    sale_amount = parse_decimal(row["Valor Venda"])
                    down_payment = parse_decimal(row["Valor Entrada"])
                    down_payment_installment_value = parse_decimal(row["Valor Parcela Entrada"])
                    number_of_installment_down_payment = int(row["Qtd Entrada"]) if pd.notna(row["Qtd Entrada"]) else None
                    number_of_installment = int(row["Qtd Parcelas"]) if pd.notna(row["Qtd Parcelas"]) else None
                    installment_value = parse_decimal(row["Valor Parcela Financiamento"])

                    # Validação de dados obrigatórios
                    if not all([customer_name, block_name, lot_name, status, contract_date, start_date]):
                        messages.warning(self.request, f"Linha ignorada (dados incompletos) - Lote {lot_name}")
                        continue

                    # Busca objetos relacionados
                    block = get_object_or_404(Block, name=block_name, enterprise__id=self.kwargs.get('enterprise_pk'))
                    lot = get_object_or_404(Lot, lot=lot_name, block=block)
                    customer_supplier = get_object_or_404(CustomerSupplier, name__iexact=customer_name)

                    # Verifica contrato ativo
                    active_contract = SalesContract.objects.filter(lot=lot, is_active=True).first()

                    if active_contract:
                        if active_contract.contract_date == contract_date:
                            # Mesmo contrato → apenas atualiza dados
                            active_contract.customer_supplier = customer_supplier
                            active_contract.status = status
                            active_contract.start_date = start_date
                            active_contract.sale_amount = sale_amount
                            active_contract.down_payment = down_payment
                            active_contract.number_of_installment_down_payment = number_of_installment_down_payment
                            active_contract.number_of_installment = number_of_installment
                            active_contract.installment_value = installment_value
                            active_contract.updated_by_user = self.request.user
                            active_contract.save()
                            updates_contracts += 1
                        else:
                            # Contrato diferente → inativa e cria novo
                            active_contract.is_active = False
                            active_contract.updated_by_user = self.request.user
                            active_contract.save()

                            SalesContract.objects.create(
                                is_active=True,
                                contract_date=contract_date,
                                lot=lot,
                                customer_supplier=customer_supplier,
                                start_date=start_date,
                                sale_amount=sale_amount,
                                down_payment=down_payment,
                                number_of_installment_down_payment=number_of_installment_down_payment,
                                number_of_installment=number_of_installment,
                                installment_value=installment_value,
                                created_by_user=self.request.user,
                                updated_by_user=self.request.user
                            )
                            created_contracts += 1
                    else:
                        # Cria contrato novo
                        SalesContract.objects.create(
                            is_active=True,
                            contract_date=contract_date,
                            lot=lot,
                            customer_supplier=customer_supplier,
                            start_date=start_date,
                            sale_amount=sale_amount,
                            down_payment=down_payment,
                            number_of_installment_down_payment=number_of_installment_down_payment,
                            number_of_installment=number_of_installment,
                            installment_value=installment_value,
                            created_by_user=self.request.user,
                            updated_by_user=self.request.user
                        )
                        created_contracts += 1

                except Exception as e:
                    messages.error(self.request, f"Erro processando lote {row.get('Lote')}: {e}")
                    continue

            messages.success(
                self.request,
                f"{updates_contracts} contratos atualizados e {created_contracts} criados com sucesso."
            )

        except Exception as e:
            messages.error(self.request, f"Erro ao processar a planilha: {e}")
            return self.form_invalid(form)

        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('lot_list', kwargs={'enterprise_pk': self.kwargs.get('enterprise_pk')})