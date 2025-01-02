from django.shortcuts import render
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView
from django.views.generic import CreateView
from django.contrib.auth.forms import UserCreationForm


class CustomLoginView(LoginView):
    template_name = 'registration/login.html'

    def get_success_url(self):
        username = self.request.user.username
        return reverse_lazy('blog:profile', kwargs={'username': username})


class CustomRegisterView(CreateView):
    template_name = 'registration/registration_form.html'
    form_class = UserCreationForm

    def get_success_url(self):
        username = self.request.user.username
        return reverse_lazy('blog:profile', kwargs={'username': username})
