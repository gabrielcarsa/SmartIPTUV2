from django.views.generic.list import ListView
from django.contrib.auth.mixins import LoginRequiredMixin

from debits.models import Enterprise


class EnterpriseListView(LoginRequiredMixin, ListView):
    model = Enterprise
    template_name = 'enterprise/list.html'
    paginate_by = 100