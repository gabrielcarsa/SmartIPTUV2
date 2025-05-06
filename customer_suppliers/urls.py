from django.urls import path

from customer_suppliers.views import CustomerSupplierListView, CustomerSupplierCreateView, CustomerSupplierUpdateView, CustomerSupplierDeleteView


urlpatterns = [
    path('', CustomerSupplierListView.as_view(), name='customer_supplier_list'),
    path('create', CustomerSupplierCreateView.as_view(), name='customer_supplier_create'),
    path('update/<int:pk>', CustomerSupplierUpdateView.as_view(), name='customer_supplier_update'),
    path('delete/<int:pk>', CustomerSupplierDeleteView.as_view(), name='customer_supplier_delete'),

]