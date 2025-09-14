from django.shortcuts import render
from django.contrib.auth.views import LoginView
from django.db.models import Sum
from customer_suppliers.models import CustomerSupplier
from debits.models import Enterprise, Lot
from financials.models import AccountHolder, FinancialTransactionInstallment
from .forms import EmailLoginForm
from django.views.generic.base import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone

# GUEST HOME PAGE
class HomeTemplateView(TemplateView):
   template_name = 'users/home.html'

# LOGIN USER WITH EMAIL
class CustomLoginView(LoginView):
    authentication_form = EmailLoginForm

# INTENAL PAGE
class DashboardTemplateView(LoginRequiredMixin, TemplateView):
   template_name = 'users/dashboard.html'

   def get_context_data(self, **kwargs):
      context = super().get_context_data(**kwargs)
      context["total_debts"] = FinancialTransactionInstallment.objects.filter(
         financial_transaction__lot__isnull=False, 
         due_date__lte= timezone.now(),
      ).aggregate(Sum('amount'))
      context["total_debts_company"] = FinancialTransactionInstallment.objects.filter(
         financial_transaction__lot__isnull=False, 
         financial_transaction__type = 0,
         due_date__lte= timezone.now(),
      ).aggregate(Sum('amount'))
      context["total_debts_customers"] = FinancialTransactionInstallment.objects.filter(
         financial_transaction__lot__isnull=False, 
         financial_transaction__type = 1,
         due_date__lte= timezone.now(),
      ).aggregate(Sum('amount'))

      context["total_lots"] = Lot.objects.all()
      context["total_enterprise"] = Enterprise.objects.all()
      context["total_customer_supplier"] = CustomerSupplier.objects.all()
      context["company"] = AccountHolder.objects.filter(
         customer_supplier__type_customer_supplier__name__iexact='Empresa'
      ).first()


      return context

