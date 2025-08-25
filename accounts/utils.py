import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist

User = get_user_model()

def get_or_create_user(username, email, firebase_uid, email_verified=False):
    try:
        user = User.objects.get(email=email)
        return user
    except ObjectDoesNotExist:
        user = User.objects.create_user(
            username=username,
            email=email
        )
        user.set_unusable_password()
        user.save()
        return user

def firebase_sign_in(email, password):
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={settings.FIREBASE_CONFIG['apiKey']}"
    
    data = {
        'email': email,
        'password': password,
        'returnSecureToken': True
    }
    
    try:
        response = requests.post(url, json=data)
        result = response.json()
        
        if response.status_code == 200:
            return True, result
        else:
            error_message = result.get('error', {}).get('message', 'Erro de autenticação')
            return False, error_message
    except Exception as e:
        return False, f"Erro de conexão: {str(e)}"

def firebase_sign_up(email, password):
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={settings.FIREBASE_CONFIG['apiKey']}"
    
    data = {
        'email': email,
        'password': password,
        'returnSecureToken': True
    }
    
    try:
        response = requests.post(url, json=data)
        result = response.json()
        
        if response.status_code == 200:
            return True, result
        else:
            error_message = result.get('error', {}).get('message', 'Erro ao criar conta')
            return False, error_message
    except Exception as e:
        return False, f"Erro de conexão: {str(e)}"