from django.urls import path

from . import views

urlpatterns = [

    # TRANSACTIONS  
    path("financial_transaction/create", views.TransactionCreateView.as_view(), name="financial_transaction_create"),
    path("financial_transaction/list", views.TransactionInstallmentListView.as_view(), name="financial_transaction_list"),
    path("financial_transaction/delete", views.MovementListView.as_view(), name="financial_transaction_delete"),

    # INSTALLMENTS
    path("transaction_installment/amount", views.TransactionInstallmentUpdateView.as_view(), name="transaction_installment_update"),
    path("transaction_installment/settlement", views.TransactionInstallmentBulkSettlementView.as_view(), name="transaction_installment_settlement"),

    # MOVEMENTS
    path("financial_movement", views.MovementListView.as_view(), name="financial_movements_list"),

    # ACCOUNT HOLDERS
    path("account_holder/list", views.AccountHolderListView.as_view(), name="account_holder_list"),
    path("account_holder/create", views.AccountHolderCreateView.as_view(), name="account_holder_create"),

    # CHECKING ACCOUNTS
    path("account_holder/checking_account/create/<int:account_holder_id>", views.CheckingAccountCreateView.as_view(), name="checking_account_create"),
    path("account_holder/checking_account/update/<int:pk>", views.CheckingAccountUpdateView.as_view(), name="checking_account_update"),

    # CHECKING ACCOUNTS BALANCE
    path("account_holder/checking_account_balance/list/<int:account_holder_id>", views.CheckingAccountBalanceListView.as_view(), name="checking_account_balance_list"),

]