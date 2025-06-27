from django.urls import path
from debits.views import EnterpriseCreateView, EnterpriseDeleteView, EnterpriseListView, EnterpriseUpdateView, LotCreateView, LotDeleteView, LotInstallmentsListView, LotListView, LotUpdateStatementCreateView, LotUpdateStatementListView, LotUpdateView, SalesContractCancelView, SalesContractCreateView, SalesContractUpdateView


urlpatterns = [
    path('enterprise/list', EnterpriseListView.as_view(), name='enterprise_list'),
    path('enterprise/create', EnterpriseCreateView.as_view(), name='enterprise_create'),
    path('enterprise/update/<int:pk>', EnterpriseUpdateView.as_view(), name='enterprise_update'),
    path('enterprise/delete/<int:pk>', EnterpriseDeleteView.as_view(), name='enterprise_delete'),

    path('lot/list/<int:enterprise_pk>', LotListView.as_view(), name='lot_list'),
    path('lot/create/<int:enterprise_pk>', LotCreateView.as_view(), name='lot_create'),
    path('lot/update/<int:enterprise_pk>/<int:pk>', LotUpdateView.as_view(), name='lot_update'),
    path('lot/delete/<int:enterprise_pk>/<int:pk>', LotDeleteView.as_view(), name='lot_delete'),
    path('update/list', LotUpdateStatementListView.as_view(), name='lot_debits_list'),
    path('update/form', LotUpdateStatementCreateView.as_view(), name='lot_debits_create'),
    path('lot/installments/list/<int:pk>', LotInstallmentsListView.as_view(), name='lot_installment_list'),


    path('sales_contract/create/<int:enterprise_pk>/<int:lot_pk>', SalesContractCreateView.as_view(), name='sales_contract_create'),
    path('sales_contract/update/<int:enterprise_pk>/<int:pk>', SalesContractUpdateView.as_view(), name='sales_contract_update'),
    path('sales_contract/cancel/<int:enterprise_pk>/<int:pk>', SalesContractCancelView.as_view(), name='sales_contract_cancel'),


]