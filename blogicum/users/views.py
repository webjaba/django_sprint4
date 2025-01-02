from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView


class CustomLoginView(LoginView):
    template_name = 'registration/login.html'

    def get_success_url(self):
        username = self.request.user.username
        return reverse_lazy('blog:profile', kwargs={'username': username})
