from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from customer_suppliers.forms import CustomerSupplierForm
from customer_suppliers.models import CustomerSupplier
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib import messages


# List View
class CustomerSupplierListView(LoginRequiredMixin, ListView):
    model = CustomerSupplier
    template_name = 'customer_supplier/list.html'
    paginate_by = 50

# Create
class CustomerSupplierCreateView(LoginRequiredMixin, CreateView):
    model = CustomerSupplier
    form_class = CustomerSupplierForm
    template_name = 'customer_supplier/form.html'
    

    def form_valid(self, form):

        form.instance.created_by_user = self.request.user
        form.instance.updated_by_user = self.request.user

        messages.success(self.request, "Cadastrado com sucesso!")
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, "Erro ao tentar cadastrar!")
        return super().form_invalid(form)
    
    def get_success_url(self):
        return reverse_lazy('customer_supplier_list')
    
# Update
class CustomerSupplierUpdateView(LoginRequiredMixin, UpdateView):
    model = CustomerSupplier
    form_class = CustomerSupplierForm
    template_name = 'customer_supplier/form.html'

    def form_valid(self, form):
        form.instance.updated_by_user = self.request.user

        messages.success(self.request, "Atualizado com sucesso!")
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, "Erro ao atualizar!")
        return super().form_invalid(form)
    
    def get_success_url(self):
        return reverse_lazy('customer_supplier_list')
    
# Delete
class CustomerSupplierDeleteView(LoginRequiredMixin, DeleteView):
    model = CustomerSupplier
    template_name = "customer_supplier/confirm_delete.html"

    def form_valid(self, form):
        messages.success(self.request, "Excluido com sucesso!")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('customer_supplier_list')

