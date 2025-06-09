from django.urls import path
from debits.views import EnterpriseCreateView, EnterpriseDeleteView, EnterpriseListView, EnterpriseUpdateView, LotCreateView, LotDeleteView, LotListView, LotUpdateView


urlpatterns = [
    path('enterprise/list', EnterpriseListView.as_view(), name='enterprise_list'),
    path('enterprise/create', EnterpriseCreateView.as_view(), name='enterprise_create'),
    path('enterprise/update/<int:pk>', EnterpriseUpdateView.as_view(), name='enterprise_update'),
    path('enterprise/delete/<int:pk>', EnterpriseDeleteView.as_view(), name='enterprise_delete'),

    path('lot/list/<int:enterprise_pk>', LotListView.as_view(), name='lot_list'),
    path('lot/create/<int:enterprise_pk>', LotCreateView.as_view(), name='lot_create'),
    path('lot/update/<int:enterprise_pk>/<int:pk>', LotUpdateView.as_view(), name='lot_update'),
    path('lot/delete/<int:enterprise_pk>/<int:pk>', LotDeleteView.as_view(), name='lot_delete'),



]