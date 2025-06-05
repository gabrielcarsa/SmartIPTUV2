from django.urls import path
from debits.views import EnterpriseCreateView, EnterpriseDeleteView, EnterpriseListView, EnterpriseUpdateView


urlpatterns = [
    path('enterprise/list', EnterpriseListView.as_view(), name='enterprise_list'),
    path('enterprise/create', EnterpriseCreateView.as_view(), name='enterprise_create'),
    path('enterprise/update/<int:pk>', EnterpriseUpdateView.as_view(), name='enterprise_update'),
    path('enterprise/delete/<int:pk>', EnterpriseDeleteView.as_view(), name='enterprise_delete'),


]