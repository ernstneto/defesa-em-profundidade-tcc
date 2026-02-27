from django.db import models

class Comment(models.Model):
	author = models.CharField(max_length=100)
	text = models.TextField()

	def __str__(self):
		return f'Comment by {self.author}'

class BlockedIP(models.Model):
	ip_address = models.GenericIPAddressField(unique=True)
	timestamp = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.ip_address