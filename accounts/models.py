from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import post_save, post_delete, pre_delete
from django.dispatch import receiver
from firebase_config import create_firebase_user, update_firebase_user, delete_firebase_user

class CustomUser(AbstractUser):
    firebase_uid = models.CharField(
        max_length=128, 
        unique=True, 
        blank=True, 
        null=True,
        verbose_name=_('Firebase UID')
    )
    email_verified = models.BooleanField(
        default=False,
        verbose_name=_('Email verificado')
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Criado em')
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Atualizado em')
    )
    
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name=_('Grupos'),
        blank=True,
        help_text=_('Os grupos aos quais este usuário pertence.'),
        related_name="customuser_set",
        related_query_name="user",
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name=_('Permissões de usuário'),
        blank=True,
        help_text=_('Permissões específicas para este usuário.'),
        related_name="customuser_set",
        related_query_name="user",
    )
    
    class Meta:
        verbose_name = _('Usuário')
        verbose_name_plural = _('Usuários')
        ordering = ['-created_at']
    
    def __str__(self):
        return self.email or self.username

@receiver(post_save, sender=CustomUser)
def sync_user_to_firebase(sender, instance, created, **kwargs):
    if kwargs.get('raw', False) or kwargs.get('update_fields') == ['last_login']:
        return
    
    try:
        if created and not instance.firebase_uid:
            firebase_uid = create_firebase_user(
                email=instance.email,
                display_name=instance.username
            )
            if firebase_uid:
                CustomUser.objects.filter(pk=instance.pk).update(firebase_uid=firebase_uid)
        
        elif instance.firebase_uid and not created:
            update_firebase_user(
                uid=instance.firebase_uid,
                email=instance.email,
                display_name=instance.username,
                email_verified=instance.email_verified
            )
            
    except Exception as e:
        print(f"❌ Erro ao sincronizar usuário para Firebase: {e}")

@receiver(pre_delete, sender=CustomUser)
def delete_user_from_firebase(sender, instance, **kwargs):
    try:
        if instance.firebase_uid:
            delete_firebase_user(instance.firebase_uid)
    except Exception as e:
        print(f"❌ Erro ao deletar usuário do Firebase: {e}")

def disable_firebase_sync():
    post_save.disconnect(sync_user_to_firebase, sender=CustomUser)
    pre_delete.disconnect(delete_user_from_firebase, sender=CustomUser)

def enable_firebase_sync():
    post_save.connect(sync_user_to_firebase, sender=CustomUser)
    pre_delete.connect(delete_user_from_firebase, sender=CustomUser)