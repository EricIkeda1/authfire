from django.apps import AppConfig
import threading
import time
import logging

logger = logging.getLogger(__name__)

class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'
    
    def ready(self):
        from django.conf import settings
        
        is_testing = getattr(settings, 'TESTING', False)
        
        if settings.DEBUG and not is_testing:
            threading.Thread(target=self.delayed_sync, daemon=True).start()
    
    def delayed_sync(self):
        time.sleep(3) 
        try:
            from .sync_utils import sync_firebase_users
            logger.info("Iniciando sincronização automática de usuários do Firebase...")
            result = sync_firebase_users()
            if result:
                synced, created, updated = result
                logger.info(f"Sincronização concluída: {synced} sincronizados, {created} criados, {updated} atualizados")
            else:
                logger.warning("Sincronização não retornou resultados")
        except Exception as e:
            logger.error(f"Erro na sincronização automática: {e}")