from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from debits.forms import LotForm, SalesContractForm
from debits.models import Enterprise, Lot, SalesContract


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

class LotListView(LoginRequiredMixin, ListView):
    model = Lot
    template_name = 'lot/list.html'
    paginate_by = 100

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['enterprise'] = get_object_or_404(Enterprise, id=self.kwargs['enterprise_pk'])
        return context

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
    
class LotDeleteView(LoginRequiredMixin, DeleteView):
    model = Lot
    template_name = 'lot/delete.html'

    def form_valid(self, form):

        messages.success(self.request, 'Operação realizada com sucesso')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('lot_list', kwargs={'enterprise_pk': self.kwargs.get('enterprise_pk')})
    
class LotDebitsListView(LoginRequiredMixin, ListView):
    model = Lot
    template_name = 'lot/debits.html'
    

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