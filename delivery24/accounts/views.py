from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect
from django.urls import path, reverse_lazy
from .forms import SignUpForm


# class SignUpView(FormView):
#     template_name = 'accounts/form.html'
#     form_class = SignUpForm
#     success_url = reverse_lazy('core:index')
#
#     # def form_valid(self, form):
#     #     # This method is called when valid form data has been POSTed.
#     #     # It should return an HttpResponse.
#     #     #form.send_email()
#     #     print('++++++++++++++++++++++++++++++++++++++++++')
#     #     return super().form_valid(form)

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('email')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect(reverse_lazy('core:index'))
    else:
        form = SignUpForm()
    return render(request, 'accounts/form.html', {'form': form})
