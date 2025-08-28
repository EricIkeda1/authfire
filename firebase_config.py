import firebase_admin
from firebase_admin import credentials, auth, exceptions
import os
from pathlib import Path
import json
from django.conf import settings

_firebase_initialized = False
_service_account_created = False

def create_firebase_service_account_file():
    global _service_account_created
    
    if _service_account_created:
        return True
        
    try:
        service_account_data = {
            "type": os.getenv('FIREBASE_TYPE', 'service_account'),
            "project_id": os.getenv('FIREBASE_PROJECT_ID', ''),
            "private_key_id": os.getenv('FIREBASE_PRIVATE_KEY_ID', ''),
            "private_key": os.getenv('FIREBASE_PRIVATE_KEY', '').replace('\\n', '\n'),
            "client_email": os.getenv('FIREBASE_CLIENT_EMAIL', ''),
            "client_id": os.getenv('FIREBASE_CLIENT_ID', ''),
            "auth_uri": os.getenv('FIREBASE_AUTH_URI', 'https://accounts.google.com/o/oauth2/auth'),
            "token_uri": os.getenv('FIREBASE_TOKEN_URI', 'https://oauth2.googleapis.com/token'),
            "auth_provider_x509_CERT_URL": os.getenv('FIREBASE_AUTH_PROVIDER_X509_CERT_URL', 'https://www.googleapis.com/oauth2/v1/certs'),
            "client_x509_cert_url": os.getenv('FIREBASE_CLIENT_X509_CERT_URL', ''),
            "universe_domain": os.getenv('FIREBASE_UNIVERSE_DOMAIN', 'googleapis.com')
        }
        
        required_fields = ['project_id', 'private_key', 'client_email']
        for field in required_fields:
            if not service_account_data[field]:
                print(f"❌ Campo obrigatório faltando: {field}")
                return False
        
        cred_path = Path(__file__).parent / 'firebase-service-account.json'
        
        with open(cred_path, 'w') as f:
            json.dump(service_account_data, f, indent=2)
        
        print(f"✅ Arquivo firebase-service-account.json criado")
        _service_account_created = True
        return True
        
    except Exception as e:
        print(f"❌ Erro ao criar arquivo de serviço: {e}")
        return False

def initialize_firebase():
    global _firebase_initialized
    
    try:
        if firebase_admin._apps:
            if not _firebase_initialized:
                print("✅ Firebase já está inicializado")
                _firebase_initialized = True
            return True
            
        if _firebase_initialized:
            return True
            
        cred_path = Path(__file__).parent / 'firebase-service-account.json'
        
        if not cred_path.exists():
            if not _service_account_created:
                print("🔍 Criando arquivo de serviço a partir de variáveis de ambiente...")
            if not create_firebase_service_account_file():
                if not _service_account_created:
                    print("❌ Não foi possível criar o arquivo de serviço")
                return False
        
        if cred_path.exists():
            if not _firebase_initialized:
                print("✅ Arquivo de serviço encontrado!")
            cred = credentials.Certificate(str(cred_path))
            firebase_admin.initialize_app(cred)
            if not _firebase_initialized:
                print("✅ Firebase Admin inicializado com sucesso!")
            _firebase_initialized = True
            return True
        else:
            if not _firebase_initialized:
                print("❌ Arquivo de serviço do Firebase não encontrado.")
            return False
                
    except Exception as e:
        if not _firebase_initialized:
            print(f"❌ Erro ao inicializar Firebase: {e}")
        return False

def get_firebase_users():
    try:
        if not initialize_firebase():
            return []
        
        users = []
        page = auth.list_users()
        
        user_count = 0
        while page:
            for user in page.users:
                user_data = {
                    'uid': user.uid,
                    'email': user.email,
                    'email_verified': user.email_verified,
                    'display_name': user.display_name or user.email.split('@')[0],
                    'created_at': user.user_metadata.creation_timestamp,
                }
                user_count += 1
                users.append(user_data)
            
            page = page.get_next_page()
        
        if user_count > 0 and not hasattr(get_firebase_users, '_printed_count'):
            print(f"✅ {user_count} usuários encontrados no Firebase")
            get_firebase_users._printed_count = True
            
        return users
        
    except Exception as e:
        if not hasattr(get_firebase_users, '_error_printed'):
            print(f"❌ Erro ao buscar usuários do Firebase: {e}")
            get_firebase_users._error_printed = True
        return []

def get_firebase_user_uids():
    try:
        if not initialize_firebase():
            return set()
        
        uids = set()
        page = auth.list_users()
        
        while page:
            for user in page.users:
                uids.add(user.uid)
            page = page.get_next_page()
        
        return uids
        
    except Exception as e:
        print(f"❌ Erro ao buscar UIDs do Firebase: {e}")
        return set()

def create_firebase_user(email, password=None, display_name=None):
    try:
        if not initialize_firebase():
            return None
            
        user_data = {
            'email': email,
            'email_verified': False,
            'display_name': display_name or email.split('@')[0],
        }
        
        if password:
            user_data['password'] = password
        
        user = auth.create_user(**user_data)
        print(f"✅ Usuário criado no Firebase: {email}")
        return user.uid
        
    except exceptions.FirebaseError as e:
        print(f"❌ Erro ao criar usuário no Firebase: {e}")
        return None
    except Exception as e:
        print(f"❌ Erro inesperado ao criar usuário: {e}")
        return None

def update_firebase_user(uid, email=None, display_name=None, email_verified=None):
    """Atualiza um usuário no Firebase"""
    try:
        if not initialize_firebase():
            return False
            
        update_data = {}
        
        if email:
            update_data['email'] = email
        if display_name:
            update_data['display_name'] = display_name
        if email_verified is not None:
            update_data['email_verified'] = email_verified
            
        if update_data:
            auth.update_user(uid, **update_data)
            print(f"✅ Usuário atualizado no Firebase: {uid}")
            return True
            
        return False
        
    except exceptions.FirebaseError as e:
        print(f"❌ Erro ao atualizar usuário no Firebase: {e}")
        return False

def delete_firebase_user(uid):
    try:
        if not initialize_firebase():
            return False
            
        auth.delete_user(uid)
        print(f"✅ Usuário deletado do Firebase: {uid}")
        return True
        
    except exceptions.FirebaseError as e:
        print(f"❌ Erro ao deletar usuário do Firebase: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado ao deletar usuário: {e}")
        return False

def get_firebase_user_by_uid(uid):
    try:
        if not initialize_firebase():
            return None
            
        user = auth.get_user(uid)
        return {
            'uid': user.uid,
            'email': user.email,
            'email_verified': user.email_verified,
            'display_name': user.display_name,
            'created_at': user.user_metadata.creation_timestamp,
        }
        
    except exceptions.FirebaseError:
        return None
    except Exception as e:
        print(f"❌ Erro ao buscar usuário no Firebase: {e}")
        return None

try:
    if not _firebase_initialized:
        initialize_firebase()
except:
    pass