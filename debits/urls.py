from django.urls import path
from debits.views import EnterpriseListView


urlpatterns = [
    path('enterprise/list', EnterpriseListView.as_view(), name='enterprise_list'),

]