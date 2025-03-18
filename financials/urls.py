from django.urls import path

from . import views

urlpatterns = [

    # TRANSACTIONS  
    path("financial_transactions/create", views.TransactionCreateView.as_view(), name="financial_transaction_create"),
    path("financial_transactions/list", views.TransactionInstallmentListView.as_view(), name="financial_transaction_list"),
    path("financial_transactions/delete", views.MovementListView.as_view(), name="financial_transaction_delete"),

    # INSTALLMENTS
    path("transaction_installments/amount", views.TransactionInstallmentsUpdateView.as_view(), name="transaction_installment_amount"),
    path("transaction_installments/settlement", views.TransactionInstallmentsBulkSettlementView.as_view(), name="transaction_installment_settlement"),

    path("financial_movements", views.MovementListView.as_view(), name="financial_movements_list"),
]