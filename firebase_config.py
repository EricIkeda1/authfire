import firebase_admin
from firebase_admin import credentials
import os
from pathlib import Path

def initialize_firebase():
    try:
        if firebase_admin._apps:
            print("Firebase já está inicializado")
            return True
            
        cred_path = Path(__file__).parent / 'firebase-service-account.json'
        
        if cred_path.exists():
            cred = credentials.Certificate(str(cred_path))
            firebase_admin.initialize_app(cred)
            print("Firebase Admin inicializado com sucesso!")
            return True
        else:
            print("Arquivo de serviço do Firebase não encontrado.")
            print(f"Procurando em: {cred_path}")
            return False
                
    except Exception as e:
        print(f"Erro ao inicializar Firebase: {e}")
        return False

initialize_firebase()