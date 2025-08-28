from django.apps import AppConfig
import threading
import time
import logging
import sys

logger = logging.getLogger(__name__)

class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'
    
    def ready(self):
        """Executado quando o app está pronto"""
        # Importa aqui para evitar import circular
        from django.conf import settings
        
        # Verifica se estamos em modo de teste de forma segura
        is_testing = getattr(settings, 'TESTING', False)
        
        # Verifica se é o comando runserver (e não createsuperuser ou outros)
        is_runserver = self.is_runserver_command()
        is_createsuperuser = self.is_createsuperuser_command()
        
        # Verifica se já executamos a sincronização
        if hasattr(self, '_sync_executed'):
            logger.debug("✅ Sincronização já executada, ignorando...")
            return
        
        if settings.DEBUG and not is_testing and is_runserver and not is_createsuperuser:
            # Marca que já executamos a sincronização
            self._sync_executed = True
            # Sincroniza automaticamente no startup (apenas em desenvolvimento com runserver)
            threading.Thread(target=self.delayed_sync, daemon=True).start()
        else:
            logger.debug("✅ Sincronização automática ignorada")
    
    def is_runserver_command(self):
        """Verifica se o comando atual é runserver"""
        return len(sys.argv) > 1 and sys.argv[1] == 'runserver'
    
    def is_createsuperuser_command(self):
        """Verifica se o comando atual é createsuperuser"""
        return len(sys.argv) > 1 and sys.argv[1] == 'createsuperuser'
    
    def delayed_sync(self):
        """Sincronização com delay para evitar problemas de inicialização"""
        time.sleep(3)  # Aguarda 3 segundos para o Django carregar completamente
        
        try:
            from .sync_utils import sync_firebase_users
            logger.info("🔄 Iniciando sincronização automática de usuários do Firebase...")
            result = sync_firebase_users()
            if result:
                synced, created, updated = result
                logger.info(f"✅ Sincronização concluída: {synced} sincronizados, {created} criados, {updated} atualizados")
            else:
                logger.info("✅ Nenhum usuário para sincronizar")
        except Exception as e:
            logger.error(f"❌ Erro na sincronização automática: {e}")