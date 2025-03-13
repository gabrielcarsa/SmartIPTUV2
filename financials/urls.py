from django.urls import path

from . import views

urlpatterns = [

    # TRANSACTIONS  
    path("financial_transactions/create", views.FinancialMovementCreateView.as_view(), name="financial_transaction_create"),
    path("financial_transactions/list", views.FinancialTransactionInstallmentListView.as_view(), name="financial_transaction_list"),
    path("financial_transactions/delete", views.FinancialMovementListView.as_view(), name="financial_transaction_delete"),

    path("financial_movements", views.FinancialMovementListView.as_view(), name="financial_movements_list"),
]