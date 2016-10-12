from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import UserCreationForm
from django.core.urlresolvers import reverse
from django.shortcuts import render
from django.views.generic import FormView

from usermgmt import forms

class Register(FormView):
    template_name = 'registration/new.html'
    form_class = UserCreationForm

    def form_valid(self, form):
        form.save()
        new_user = authenticate(username=form.cleaned_data['username'],
                                password=form.cleaned_data['password1'])
        login(self.request, new_user)
        return super(Register, self).form_valid(form)

    def get_success_url(self):
        return self.request.POST.get(
            'next', self.request.GET.get('next', reverse('front')))
