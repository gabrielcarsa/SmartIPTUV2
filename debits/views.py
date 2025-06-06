from django.urls import reverse_lazy
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from debits.models import Enterprise


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
