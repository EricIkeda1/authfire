from firebase_config import get_firebase_users
from .models import CustomUser
from django.utils import timezone
from django.db import transaction
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def convert_firebase_timestamp(timestamp):
    try:
        if isinstance(timestamp, (int, float)):
            if timestamp > 1e12:  
                timestamp = timestamp / 1000
            return timezone.make_aware(datetime.fromtimestamp(timestamp))
        elif hasattr(timestamp, 'utcoffset'):
            return timestamp
        else:
            return timezone.now()
    except (ValueError, TypeError, OSError) as e:
        logger.warning(f"⚠️ Erro ao converter timestamp {timestamp}: {e}")
        return timezone.now()

def sync_firebase_users():
    try:
        firebase_users = get_firebase_users()
        
        if not firebase_users:
            logger.warning("Nenhum usuário encontrado no Firebase ou Firebase não configurado")
            return 0, 0, 0
        
        logger.info(f"Encontrados {len(firebase_users)} usuários no Firebase")
        
        synced_count = 0
        created_count = 0
        updated_count = 0
        
        with transaction.atomic():
            for firebase_user in firebase_users:
                try:
                    if not firebase_user.get('email'):
                        logger.warning(f"Usuário sem email: {firebase_user.get('uid')}")
                        continue
                    
                    email = firebase_user['email']
                    uid = firebase_user['uid']
                    
                    user = None
                    created = False
                    
                    if uid:
                        try:
                            user = CustomUser.objects.get(firebase_uid=uid)
                            logger.debug(f"✅ Usuário encontrado por UID: {email}")
                        except CustomUser.DoesNotExist:
                            pass
                    
                    if not user:
                        try:
                            user = CustomUser.objects.get(email=email)
                            logger.debug(f"✅ Usuário encontrado por email: {email}")
                        except CustomUser.DoesNotExist:
                            pass
                    
                    if not user:
                        user = CustomUser()
                        created = True
                        created_count += 1
                        logger.info(f"🎉 NOVO usuário criado: {email}")
                    
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
                    
                    if display_name and not created:
                        names = display_name.split(' ', 1)
                        if len(names) > 0 and user.first_name != names[0]:
                            user.first_name = names[0]
                            needs_update = True
                        if len(names) > 1 and user.last_name != names[1]:
                            user.last_name = names[1]
                            needs_update = True
                    
                    if created or needs_update:
                        if not created:
                            updated_count += 1
                            logger.info(f"🔄 Usuário atualizado: {email}")
                        
                        user.set_unusable_password()
                        user.save()
                    
                    synced_count += 1
                    
                except Exception as e:
                    logger.error(f"❌ Erro ao processar usuário {firebase_user.get('email', 'unknown')}: {e}")
                    continue
        
        logger.info(f"📊 Sincronização concluída!")
        logger.info(f"✅ Total sincronizado: {synced_count}")
        logger.info(f"🎉 Novos usuários: {created_count}")
        logger.info(f"🔄 Usuários atualizados: {updated_count}")
        
        return synced_count, created_count, updated_count
        
    except Exception as e:
        logger.error(f"❌ Erro durante a sincronização: {e}")
        return 0, 0, 0


def update_existing_users():
    try:
        firebase_users = get_firebase_users()
        
        if not firebase_users:
            logger.warning("Nenhum usuário encontrado no Firebase")
            return 0
        
        updated_count = 0
        
        with transaction.atomic():
            for firebase_user in firebase_users:
                try:
                    email = firebase_user.get('email')
                    uid = firebase_user.get('uid')
                    
                    if not email or not uid:
                        continue
                    
                    existing_users = CustomUser.objects.filter(email=email)
                    
                    for user in existing_users:
                        needs_update = False
                        
                        if not user.firebase_uid:
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
                            logger.info(f"🔄 Dados antigos atualizados: {user.email}")
                            
                except Exception as e:
                    logger.error(f"Erro ao atualizar usuário existente: {e}")
                    continue
        
        logger.info(f"✅ Atualização de dados antigos concluída: {updated_count} usuários atualizados")
        return updated_count
        
    except Exception as e:
        logger.error(f"Erro durante atualização de dados antigos: {e}")
        return 0