import firebase_admin
from firebase_admin import auth
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist

User = get_user_model()

def firebase_sign_in(email, password):
    import requests
    
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
    import requests
    
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

def get_or_create_user(email, firebase_uid, email_verified=False):
    try:
        user = User.objects.get(firebase_uid=firebase_uid)
        return user
    except ObjectDoesNotExist:
        try:
            user = User.objects.get(email=email)
            user.firebase_uid = firebase_uid
            user.email_verified = email_verified
            user.save()
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
                email=email,
                firebase_uid=firebase_uid,
                email_verified=email_verified
            )
            user.set_unusable_password()  
            user.save()
            return user

def verify_firebase_token(id_token):
    try:
        decoded_token = auth.verify_id_token(id_token)
        return {
            'uid': decoded_token['uid'],
            'email': decoded_token.get('email'),
            'email_verified': decoded_token.get('email_verified', False)
        }
    except Exception as e:
        print(f"Erro ao verificar token: {e}")
        return None

def create_firebase_user(email, password):
    try:
        user = auth.create_user(
            email=email,
            password=password,
            email_verified=False
        )
        return True, user
    except Exception as e:
        return False, str(e)

def get_firebase_user(uid):
    try:
        user = auth.get_user(uid)
        return True, user
    except Exception as e:
        return False, str(e)