from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

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