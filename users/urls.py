from django.urls import include, path
from . import views

urlpatterns = [
    path("dashboard/", views.DashboardTemplateView.as_view(), name="dashboard"), 
]