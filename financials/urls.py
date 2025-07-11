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
    path("financial_movement/order", views.MovementUpdateOrderView.as_view(), name="financial_movements_order"),
    path("financial_movement/report", views.MovementListPDF.as_view(), name="financial_movements_list_pdf"),
    path("financial_movement/import-ofx", views.MovementImportOFXView.as_view(), name="financial_movements_import"),
    path("financial_movement/import-save", views.MovementImportSaveView.as_view(), name="financial_movements_save"),

    # ACCOUNT HOLDERS
    path("account_holder/list", views.AccountHolderListView.as_view(), name="account_holder_list"),
    path("account_holder/create", views.AccountHolderCreateView.as_view(), name="account_holder_create"),

    # CHECKING ACCOUNTS
    path("account_holder/checking_account/create/<int:account_holder_id>", views.CheckingAccountCreateView.as_view(), name="checking_account_create"),
    path("account_holder/checking_account/update/<int:account_holder_id>/<int:pk>", views.CheckingAccountUpdateView.as_view(), name="checking_account_update"),

    # CHECKING ACCOUNTS BALANCE
    path("account_holder/checking_account_balance/list/<int:account_holder_id>", views.CheckingAccountBalanceListView.as_view(), name="checking_account_balance_list"),

    # FINANCIAL CATEGORY
    path("financial_category/list", views.FinancialCategoryListView.as_view(), name="financial_category_list"),
    path("financial_category/create", views.FinancialCategoryCreateView.as_view(), name="financial_category_create"),
    path("financial_category/update/<int:pk>", views.FinancialCategoryUpdateView.as_view(), name="financial_category_update"),

]