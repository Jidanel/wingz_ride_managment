from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from .forms import CustomUserCreationForm

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account created successfully! You can now login.')
            return redirect('login')
    else:
        form = CustomUserCreationForm()
        # Si l'utilisateur est authentifié, préremplir l'email
        if request.user.is_authenticated:
            form.fields['email'].initial = request.user.email
    return render(request, 'users/register.html', {'form': form})

