# accounts/middleware.py

from django.contrib.auth import logout
from django.shortcuts import redirect
from django.contrib import messages
import logging

logger = logging.getLogger('django')

class SessionIPProtectionMiddleware:
    """
    Middleware para garantir que a sessão do usuário esteja amarrada ao seu IP.
    Se o IP mudar durante a sessão, o usuário é deslogado forçadamente.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def _get_client_ip(self, request):
        """
        Função auxiliar para descobrir o IP real, com suporte a Cloudflare e Proxy.
        """
        # 1. Tenta pegar o IP real da Cloudflare
        cf_ip = request.META.get('HTTP_CF_CONNECTING_IP')
        if cf_ip:
            return cf_ip

        # 2. Tenta pegar do X-Forwarded-For (Nginx/Ngrok)
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()

        # 3. Fallback para o endereço remoto direto
        return request.META.get('REMOTE_ADDR')

    def __call__(self, request):
        # CORREÇÃO AQUI: É 'request.user.is_authenticated', não 'request.user_is_authenticated'
        if request.user.is_authenticated:
            current_ip = self._get_client_ip(request)
            
            session_ip = request.session.get('session_ip_address')

            if not session_ip:
                # Salva o IP inicial
                request.session['session_ip_address'] = current_ip
            
            elif current_ip != session_ip:
                # IP mudou! Encerra a sessão.
                logger.warning(f"SEGURANÇA: Sessão invalidada. IP mudou de {session_ip} para {current_ip}. Usuário: {request.user.username}")
                
                logout(request)
                messages.error(request, "Sua sessão foi encerrada por segurança porque seu endereço IP mudou.")
                return redirect('accounts:login')

        response = self.get_response(request)
        return response