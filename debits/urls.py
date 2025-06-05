from django.urls import path
from debits.views import EnterpriseCreateView, EnterpriseListView


urlpatterns = [
    path('enterprise/list', EnterpriseListView.as_view(), name='enterprise_list'),
    path('enterprise/create', EnterpriseCreateView.as_view(), name='enterprise_create'),

]