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

    def get_queryset(self):
        return super().get_queryset().order_by('name')

# Create
class CustomerSupplierCreateView(LoginRequiredMixin, CreateView):
    model = CustomerSupplier
    form_class = CustomerSupplierForm
    template_name = 'customer_supplier/form.html'
    

    def form_valid(self, form):

        # selected types
        types = form.cleaned_data['type_customer_supplier']

        # for in types
        for t in types:

            if t.name.lower() == 'empresa':

                # get the Company register
                customer_supplier_company = CustomerSupplier.objects.filter(type_customer_supplier__name__iexact='Empresa').first()
               
                if customer_supplier_company:
                    messages.error(self.request, "Só pode ter um cadastro de Empresa no sistema!")
                    return super().form_invalid(form)
                
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

        # selected types
        types = form.cleaned_data['type_customer_supplier']

        # update object
        obj = self.get_object()

        # for in types
        for t in types:

            if t.name.lower() == 'empresa':

                # get the Company register
                customer_supplier_company = CustomerSupplier.objects.filter(type_customer_supplier__name__iexact='Empresa').first()
               
                if customer_supplier_company and obj != customer_supplier_company:
                    messages.error(self.request, "Só pode ter um cadastro de Empresa no sistema!")
                    return super().form_invalid(form)
                
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

