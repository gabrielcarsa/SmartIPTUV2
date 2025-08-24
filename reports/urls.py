from django.urls import path

from . import views

urlpatterns = [
    path("portfolio-years", views.PortfolioYearsFormView.as_view(), name="portfolio_years"),

]