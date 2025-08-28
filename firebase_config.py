import firebase_admin
from firebase_admin import credentials, auth
import os
from pathlib import Path
import json
from django.conf import settings

def create_firebase_service_account_file():
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
            "auth_provider_x509_cert_url": os.getenv('FIREBASE_AUTH_PROVIDER_X509_CERT_URL', 'https://www.googleapis.com/oauth2/v1/certs'),
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
        
        print(f"✅ Arquivo firebase-service-account.json criado em: {cred_path}")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao criar arquivo de serviço: {e}")
        return False

def initialize_firebase():
    try:
        if firebase_admin._apps:
            print("✅ Firebase já está inicializado")
            return True
            
        cred_path = Path(__file__).parent / 'firebase-service-account.json'
        
        if not cred_path.exists():
            print("🔍 Arquivo de serviço não encontrado, criando a partir de variáveis de ambiente...")
            if not create_firebase_service_account_file():
                print("❌ Não foi possível criar o arquivo de serviço")
                return False
        
        if cred_path.exists():
            print("✅ Arquivo de serviço encontrado!")
            cred = credentials.Certificate(str(cred_path))
            firebase_admin.initialize_app(cred)
            print("✅ Firebase Admin inicializado com sucesso!")
            return True
        else:
            print("❌ Arquivo de serviço do Firebase não encontrado.")
            return False
                
    except Exception as e:
        print(f"❌ Erro ao inicializar Firebase: {e}")
        return False

def parse_firebase_timestamp(timestamp):
    try:
        if hasattr(timestamp, 'timestamp'):
            return timestamp
        elif isinstance(timestamp, (int, float)):
            if timestamp > 1e12:
                timestamp = timestamp / 1000
            return timestamp
        else:
            return None
    except Exception as e:
        print(f"Erro ao converter timestamp: {e}")
        return None

def get_firebase_users():
    try:
        print("🔄 Tentando buscar usuários do Firebase...")
        
        if not initialize_firebase():
            print("❌ Firebase não inicializado, não é possível buscar usuários")
            return []
        
        print("✅ Firebase inicializado, listando usuários...")
        users = []
        page = auth.list_users()
        
        print(f"📄 Primeira página de usuários encontrada")
        
        while page:
            for user in page.users:
                user_data = {
                    'uid': user.uid,
                    'email': user.email,
                    'email_verified': user.email_verified,
                    'display_name': user.display_name or user.email.split('@')[0],
                    'created_at': parse_firebase_timestamp(user.user_metadata.creation_timestamp),
                }
                print(f"👤 Usuário encontrado: {user_data['email']}")
                users.append(user_data)
            
            page = page.get_next_page()
            if page:
                print("📄 Próxima página encontrada...")
        
        print(f"✅ Total de {len(users)} usuários encontrados no Firebase")
        return users
        
    except Exception as e:
        print(f"❌ Erro ao buscar usuários do Firebase: {e}")
        import traceback
        traceback.print_exc()
        return []
    
print("🚀 Inicializando Firebase...")
firebase_initialized = initialize_firebase()