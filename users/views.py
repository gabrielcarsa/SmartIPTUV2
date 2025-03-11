from django.shortcuts import render
from django.contrib.auth.views import LoginView
from .forms import EmailLoginForm
from django.views.generic.base import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

# GUEST HOME PAGE
class HomeTemplateView(TemplateView):
   template_name = 'users/home.html'

# LOGIN USER WITH EMAIL
class CustomLoginView(LoginView):
    authentication_form = EmailLoginForm

# INTENAL PAGE
class DashboardTemplateView(LoginRequiredMixin, TemplateView):
   template_name = 'users/dashboard.html'

