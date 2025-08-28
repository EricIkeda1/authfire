from firebase_config import get_firebase_users, get_firebase_user_uids
from .models import CustomUser, disable_firebase_sync, enable_firebase_sync
from django.utils import timezone
from django.db import transaction
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def convert_firebase_timestamp(timestamp):
    try:
        if timestamp is None:
            return timezone.now()
            
        if isinstance(timestamp, (int, float)):
            if timestamp > 1e12:
                timestamp = timestamp / 1000
            return timezone.make_aware(datetime.fromtimestamp(timestamp))
        elif hasattr(timestamp, 'utcoffset'):
            return timestamp
        else:
            return timezone.now()
    except (ValueError, TypeError, OSError) as e:
        logger.warning(f"⚠️ Erro ao converter timestamp: {e}")
        return timezone.now()

def sync_firebase_users():
    try:
        disable_firebase_sync()
        
        firebase_uids = get_firebase_user_uids()
        logger.info(f"✅ {len(firebase_uids)} UIDs encontrados no Firebase")
        
        firebase_users = get_firebase_users()
        
        if not firebase_users:
            logger.info("✅ Nenhum usuário encontrado no Firebase para sincronizar")
            return 0, 0, 0, 0
        
        logger.info(f"✅ {len(firebase_users)} usuários encontrados no Firebase")
        
        synced_count = 0
        created_count = 0
        updated_count = 0
        deleted_count = 0
        
        with transaction.atomic():
            for firebase_user in firebase_users:
                try:
                    if not firebase_user.get('email'):
                        continue
                    
                    email = firebase_user['email']
                    uid = firebase_user['uid']
                    
                    user = None
                    created = False
                    
                    if uid:
                        try:
                            user = CustomUser.objects.get(firebase_uid=uid)
                        except CustomUser.DoesNotExist:
                            pass
                    
                    if not user:
                        try:
                            user = CustomUser.objects.get(email=email)
                        except CustomUser.DoesNotExist:
                            pass
                    
                    if not user:
                        user = CustomUser()
                        created = True
                        created_count += 1
                    
                    needs_update = False
                    
                    if not user.firebase_uid or user.firebase_uid != uid:
                        user.firebase_uid = uid
                        needs_update = True
                    
                    if user.email != email:
                        user.email = email
                        needs_update = True
                    
                    email_verified = firebase_user.get('email_verified', False)
                    if user.email_verified != email_verified:
                        user.email_verified = email_verified
                        needs_update = True
                    
                    display_name = firebase_user.get('display_name', '')
                    new_username = display_name or email.split('@')[0]
                    if user.username != new_username:
                        user.username = new_username[:150]
                        needs_update = True
                    
                    created_at = firebase_user.get('created_at')
                    if created or not user.date_joined:
                        user.date_joined = convert_firebase_timestamp(created_at)
                        needs_update = True
                    
                    if created or needs_update:
                        if not created:
                            updated_count += 1
                        
                        user.set_unusable_password()
                        user.save()
                    
                    synced_count += 1
                    
                except Exception as e:
                    logger.error(f"❌ Erro ao processar {firebase_user.get('email', 'unknown')}: {e}")
                    continue
            
            django_users_with_firebase = CustomUser.objects.exclude(firebase_uid__isnull=True).exclude(firebase_uid='')
            
            for django_user in django_users_with_firebase:
                if django_user.firebase_uid not in firebase_uids:
                    try:
                        logger.info(f"🗑️  Deletando usuário órfão: {django_user.email} (UID: {django_user.firebase_uid})")
                        django_user.delete()
                        deleted_count += 1
                    except Exception as e:
                        logger.error(f"❌ Erro ao deletar usuário órfão {django_user.email}: {e}")
        
        logger.info(f"📊 Sincronização completa concluída!")
        logger.info(f"✅ Total sincronizado: {synced_count}")
        logger.info(f"🎉 Novos usuários: {created_count}")
        logger.info(f"🔄 Usuários atualizados: {updated_count}")
        logger.info(f"🗑️  Usuários deletados (órfãos): {deleted_count}")
        
        return synced_count, created_count, updated_count, deleted_count
        
    except Exception as e:
        logger.error(f"❌ Erro durante a sincronização: {e}")
        return 0, 0, 0, 0
    finally:
        enable_firebase_sync()

def delete_orphaned_users():
    try:
        disable_firebase_sync()
        
        firebase_uids = get_firebase_user_uids()
        deleted_count = 0
        
        django_users_with_firebase = CustomUser.objects.exclude(firebase_uid__isnull=True).exclude(firebase_uid='')
        
        for django_user in django_users_with_firebase:
            if django_user.firebase_uid not in firebase_uids:
                try:
                    logger.info(f"🗑️  Deletando usuário órfão: {django_user.email}")
                    django_user.delete()
                    deleted_count += 1
                except Exception as e:
                    logger.error(f"❌ Erro ao deletar usuário órfão {django_user.email}: {e}")
        
        logger.info(f"✅ {deleted_count} usuários órfãos deletados")
        return deleted_count
        
    except Exception as e:
        logger.error(f"❌ Erro ao deletar usuários órfãos: {e}")
        return 0
    finally:
        enable_firebase_sync()

def update_existing_users():
    try:
        disable_firebase_sync()
        
        firebase_users = get_firebase_users()
        if not firebase_users:
            logger.info("✅ Nenhum usuário encontrado no Firebase para atualizar")
            return 0
        
        updated_count = 0
        
        with transaction.atomic():
            for firebase_user in firebase_users:
                try:
                    if not firebase_user.get('email') or not firebase_user.get('uid'):
                        continue
                    
                    email = firebase_user['email']
                    uid = firebase_user['uid']
                    
                    try:
                        user = CustomUser.objects.get(email=email)
                    except CustomUser.DoesNotExist:
                        continue
                    
                    needs_update = False
                    
                    if user.firebase_uid != uid:
                        user.firebase_uid = uid
                        needs_update = True
                    
                    email_verified = firebase_user.get('email_verified', False)
                    if user.email_verified != email_verified:
                        user.email_verified = email_verified
                        needs_update = True
                    
                    display_name = firebase_user.get('display_name', '')
                    new_username = display_name or email.split('@')[0]
                    if user.username != new_username:
                        user.username = new_username[:150]
                        needs_update = True
                    
                    if needs_update:
                        user.save()
                        updated_count += 1
                        logger.info(f"🔄 Usuário atualizado: {email}")
                    
                except Exception as e:
                    logger.error(f"❌ Erro ao atualizar {firebase_user.get('email', 'unknown')}: {e}")
                    continue
        
        logger.info(f"✅ {updated_count} usuários atualizados")
        return updated_count
        
    except Exception as e:
        logger.error(f"❌ Erro durante a atualização: {e}")
        return 0
    finally:
        enable_firebase_sync()