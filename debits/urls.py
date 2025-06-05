from django.urls import path
from debits.views import EnterpriseCreateView, EnterpriseListView, EnterpriseUpdateView


urlpatterns = [
    path('enterprise/list', EnterpriseListView.as_view(), name='enterprise_list'),
    path('enterprise/create', EnterpriseCreateView.as_view(), name='enterprise_create'),
    path('enterprise/update/<int:pk>', EnterpriseUpdateView.as_view(), name='enterprise_update'),

]