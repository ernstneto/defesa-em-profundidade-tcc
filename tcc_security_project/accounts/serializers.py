# accounts/serializers.py
from rest_framework import serializers
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    # ATENÇÃO: A classe Meta deve estar "dentro" da classe UserSerializer
    # (com 4 espaços de recuo)
    class Meta:
        model = User
        # A lista de campos deve estar dentro da Meta (com 8 espaços de recuo)
        fields = ['id', 'username', 'email', 'first_name', 'last_name']