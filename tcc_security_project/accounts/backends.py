# accounts/backends.py

from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

UserModel = get_user_model()

class EmailOrUsernameBackend(ModelBackend):
    """
    Backend de autenticação customizado que permite login
    usando tanto o nome de usuário quanto o endereço de e-mail.
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # Tenta encontrar o usuário buscando pelo username OU pelo email (case-insensitive)
            user = UserModel.objects.get(Q(username__iexact=username) | Q(email__iexact=username))
        except UserModel.DoesNotExist:
            return None
        except UserModel.MultipleObjectsReturned:
             # Retorna None por segurança se emails não forem únicos (improvável com User padrão)
             return None
        else:
            # Este bloco 'else' só executa se o 'try' foi bem-sucedido (usuário encontrado)
            # Verifica a senha E se o usuário pode autenticar (está ativo, etc.)
            if user.check_password(password) and self.user_can_authenticate(user):
                return user
        # Se a senha/verificação no 'else' falhou, ou o try falhou antes, retorna None
        return None

    def get_user(self, user_id):
        try:
            return UserModel.objects.get(pk=user_id)
        except UserModel.DoesNotExist:
            return None