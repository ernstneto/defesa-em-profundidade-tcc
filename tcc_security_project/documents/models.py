# documents/models.py
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.core.files.base import ContentFile
from cryptography.fernet import Fernet
import hashlib
import os

class Document(models.Model):
    LEVEL_CHOICES = [
        ('PUBLIC', 'Público (Acesso Livre)'),
        ('INTERNAL', 'Interno (Requer Login)'),
        ('CONFIDENTIAL', 'Confidencial (Requer VPN)'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    # Campo opcional para permitir criar via texto
    file = models.FileField(upload_to='secure_docs/', blank=True, null=True)
    classification = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='INTERNAL')
    
    # Correção do nome do campo de data (upload_at vs uploaded_at)
    # Vamos manter 'upload_at' se foi assim que ficou no banco, ou 'uploaded_at'
    # Se seu banco já tem 'upload_at', mantenha. Se tiver 'uploaded_at', use este.
    # Vou usar 'upload_at' baseado no seu erro anterior.
    upload_at = models.DateTimeField(auto_now_add=True) 
    
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # Auditoria e Segurança
    file_hash = models.CharField(max_length=64, blank=True, editable=False)
    is_encrypted = models.BooleanField(default=False, editable=False)

    def save(self, *args, **kwargs):
        # Criptografia automática no Upload
        if self.file and not self.is_encrypted:
            try:
                # 1. Ler o arquivo original
                self.file.open('rb')
                original_content = self.file.read()
                
                # 2. Gerar Hash
                self.file_hash = hashlib.sha256(original_content).hexdigest()
                
                # 3. Criptografar
                f = Fernet(settings.ENCRYPTION_KEY)
                encrypted_content = f.encrypt(original_content)
                
                # 4. Salvar criptografado
                new_name = f"{self.file.name}.enc"
                self.file.save(new_name, ContentFile(encrypted_content), save=False)
                self.is_encrypted = True
                self.file.close()
            except Exception as e:
                print(f"Erro ao criptografar: {e}")
            
        super().save(*args, **kwargs)

    # --- O MÉTODO QUE ESTAVA FALTANDO ---
    def get_decrypted_content(self):
        """Descriptografa na memória para download"""
        if not self.file:
            return b""
            
        self.file.open('rb')
        content = self.file.read()
        
        if not self.is_encrypted:
            return content
            
        try:
            f = Fernet(settings.ENCRYPTION_KEY)
            return f.decrypt(content)
        except Exception as e:
            # Se der erro na descriptografia (chave errada?), retorna vazio ou lança erro
            print(f"Erro ao descriptografar: {e}")
            raise e

    def __str__(self):
        return f"[{self.classification}] {self.title}"

class AccessLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    document = models.ForeignKey(Document, on_delete=models.CASCADE)
    action = models.CharField(max_length=50)
    ip_address = models.GenericIPAddressField()
    timestamp = models.DateTimeField(auto_now_add=True)
    success = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.user} - {self.action} - {self.document.title}"