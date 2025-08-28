from django.core.management.base import BaseCommand
from accounts.sync_utils import sync_firebase_users, update_existing_users, delete_orphaned_users

class Command(BaseCommand):
    help = 'Sincroniza usuários do Firebase com o Django - sincronização bidirecional completa'
    
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
        parser.add_argument(
            '--delete-orphans',
            action='store_true',
            help='Deleta apenas usuários órfãos (que não existem no Firebase)',
        )
    
    def handle(self, *args, **options):
        force = options['force']
        update_existing_only = options['update_existing']
        delete_orphans_only = options['delete_orphans']
        
        from django.conf import settings
        if not force and not settings.DEBUG:
            self.stdout.write(
                self.style.WARNING(
                    '⚠️  Execução em modo produção. Use --force para confirmar.'
                )
            )
            return
        
        if delete_orphans_only:
            self.stdout.write('🗑️  Deletando usuários órfãos...')
            deleted = delete_orphaned_users()
            self.stdout.write(
                self.style.SUCCESS(
                    f'✅ Deleção de órfãos concluída! '
                    f'Usuários deletados: {deleted}'
                )
            )
        elif update_existing_only:
            self.stdout.write('🔄 Forçando atualização de dados antigos...')
            updated = update_existing_users()
            self.stdout.write(
                self.style.SUCCESS(
                    f'✅ Atualização de dados antigos concluída! '
                    f'Usuários atualizados: {updated}'
                )
            )
        else:
            self.stdout.write('🔄 Iniciando sincronização completa bidirecional...')
            synced, created, updated, deleted = sync_firebase_users()
            self.stdout.write(
                self.style.SUCCESS(
                    f'✅ Sincronização bidirecional concluída! '
                    f'Total: {synced}, Criados: {created}, Atualizados: {updated}, Deletados: {deleted}'
                )
            )