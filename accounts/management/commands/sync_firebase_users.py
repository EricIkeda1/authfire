from django.core.management.base import BaseCommand
from accounts.sync_utils import sync_firebase_users, update_existing_users

class Command(BaseCommand):
    help = 'Sincroniza usuários do Firebase com o Django - atualiza dados antigos também'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Força a sincronização mesmo em produção',
        )
        parser.add_argument(
            '--update-existing',
            action='store_true',
            help='Força a atualização de dados antigos apenas',
        )
    
    def handle(self, *args, **options):
        force = options['force']
        update_existing_only = options['update_existing']
        
        from django.conf import settings
        if not force and not settings.DEBUG:
            self.stdout.write(
                self.style.WARNING(
                    '⚠️  Execução em modo produção. Use --force para confirmar.'
                )
            )
            return
        
        if update_existing_only:
            self.stdout.write('🔄 Forçando atualização de dados antigos...')
            updated = update_existing_users()
            self.stdout.write(
                self.style.SUCCESS(
                    f'✅ Atualização de dados antigos concluída! '
                    f'Usuários atualizados: {updated}'
                )
            )
        else:
            self.stdout.write('🔄 Iniciando sincronização completa de usuários do Firebase...')
            synced, created, updated = sync_firebase_users()
            self.stdout.write(
                self.style.SUCCESS(
                    f'✅ Sincronização concluída! '
                    f'Total: {synced}, Criados: {created}, Atualizados: {updated}'
                )
            )