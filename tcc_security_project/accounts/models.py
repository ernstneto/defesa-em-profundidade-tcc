from django.db import models
from django.contrib.auth.models import User
import secrets
from django.utils import timezone

class LoginHistory(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	ip_address = models.GenericIPAddressField()
	timestamp = models.DateTimeField(auto_now_add=True)
	country = models.CharField(max_length=100, null=True, blank=True)
	city = models.CharField(max_length=100, null=True, blank=True)

	def __str__(self):
		return f"{self.username} logged in from {self.ip_address} ({self.country} at {self.timestamp}.)"

# --- MODELO para BLACKLIST ---
class BlockedIP(models.Model):
	ip_address = models.GenericIPAddressField(unique=True)
	timestamp = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.ip_address

# --- MODELO para BLOCKEDNETWORK ---
class BlockedNetwork(models.Model):
	# armazena a rede em notação CIDR como texto (ex: "192.168.1.0/24")
	network = models.CharField(max_length=50, unique=True, db_index=True)
	timestamp = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.network

# ---- MODELO PARA MUDANÇA SEGURA DE E-MAIL ----
class PendingEmailChange(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, related_name='pending_email_change')
	new_email = models.EmailField(unique=True)
	confirmation_token = models.CharField(max_length=64, unique=True)
	created_at = models.DateTimeField(auto_now_add=True)
	expires_at = models.DateTimeField() #Definir o tempo de expiracao na view

	def save(self, *args, **kwargs):
		# Gera um token seguro se não houver um
		if not self.confirmation_token:
			self.confirmation_token = secrets.token_urlsafe(32)

		# Define a expiração para, por exemplo, 24 horas a partir de agora
		if not self.expires_at:
			self.expires_at = timezone.now() + timezone.timedelta(days=1)

		super().save(*args, **kwargs)

	def is_expired(self):
		""" Verifica se o token já expirou. """
		return timezone.now() > self.expires_at

	def __str__(self):
		return f"Solicitação de {self.user.username} para {self.new_email}"
