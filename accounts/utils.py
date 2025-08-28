import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from .sync_utils import sync_firebase_users 

User = get_user_model()

def get_or_create_user(username, email, firebase_uid, email_verified=False):
    try:
        try:
            user = User.objects.get(firebase_uid=firebase_uid)
            print(f"✅ Usuário encontrado por UID: {user.email}")
            return user
        except (ObjectDoesNotExist, AttributeError):
            pass
        
        user = User.objects.get(email=email)
        print(f"✅ Usuário encontrado por email: {user.email}")
        
        try:
            if hasattr(user, 'firebase_uid') and not user.firebase_uid:
                user.firebase_uid = firebase_uid
                user.email_verified = email_verified
                user.save()
                print(f"🔄 UID adicionado ao usuário existente: {user.email}")
        except AttributeError:
            pass
            
        return user
        
    except ObjectDoesNotExist:
        username = email.split('@')[0]  
        counter = 1
        original_username = username
        
        while User.objects.filter(username=username).exists():
            username = f"{original_username}{counter}"
            counter += 1
        
        user = User.objects.create_user(
            username=username,
            email=email
        )
        
        try:
            user.firebase_uid = firebase_uid
            user.email_verified = email_verified
        except AttributeError:
            pass
            
        user.set_unusable_password()  
        user.save()
        
        print(f"🎉 NOVO usuário criado no Django: {email}")
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

def sync_users_command():
    from .sync_utils import sync_firebase_users
    return sync_firebase_users()