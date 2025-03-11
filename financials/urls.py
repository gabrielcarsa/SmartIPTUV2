from django.urls import path

from . import views

urlpatterns = [
    path("financial_movements", views.FinancialMovementListView.as_view(), name="financial_movements"),
]