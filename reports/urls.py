from django.urls import path

from . import views

urlpatterns = [
    path("portfolio-years/data", views.PortfolioYearsDataView.as_view(), name="portfolio_years_data"),
    path('portfolio-years', views.PortfolioYearsTemplateView.as_view(), name='portfolio_years'),


]