from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .utils import firebase_sign_in, firebase_sign_up, get_or_create_user

def home(request):
    return render(request, 'home.html')

def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        if not email or not password:
            messages.error(request, 'Por favor, preencha todos os campos.')
            return render(request, 'login.html')
        
        success, result = firebase_sign_in(email, password)
        
        if success:
            user = get_or_create_user(
                username=email.split('@')[0],
                email=email,
                firebase_uid=result['localId'],
                email_verified=False
            )
            login(request, user)
            messages.success(request, 'Login realizado com sucesso!')
            return redirect('home')
        else:
            messages.error(request, result)
    
    return render(request, 'login.html')

def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        
        if not email or not password or not confirm_password:
            messages.error(request, 'Por favor, preencha todos os campos.')
            return render(request, 'register.html')
        
        if password != confirm_password:
            messages.error(request, 'As senhas não coincidem.')
            return render(request, 'register.html')
        
        if len(password) < 6:
            messages.error(request, 'A senha deve ter pelo menos 6 caracteres.')
            return render(request, 'register.html')
        
        success, result = firebase_sign_up(email, password)
        
        if success:
            user = get_or_create_user(
                username=email.split('@')[0],
                email=email,
                firebase_uid=result['localId'],
                email_verified=False
            )
            login(request, user)
            messages.success(request, 'Conta criada com sucesso!')
            return redirect('home')
        else:
            messages.error(request, result)
    
    return render(request, 'register.html')

def logout_view(request):
    logout(request)
    messages.success(request, 'Logout realizado com sucesso!')
    return redirect('home')