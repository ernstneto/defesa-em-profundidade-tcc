# comments/middleware.py

import time
import logging
import ipaddress
from django.core.cache import cache
from django.http import HttpResponseForbidden
from accounts.models import BlockedIP, BlockedNetwork

blacklist_logger = logging.getLogger('blacklist_events')

class RateLimitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 1. Obter o IP
        ip_address = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR'))
        if ip_address:
            ip_address = ip_address.split(',')[0].strip()
        
        # 2. Bloqueio de IP Vazio/Inválido
        if not ip_address or ip_address.lower() == 'unknown':
            return HttpResponseForbidden('<h1>Acesso Negado: Origem não identificada.</h1>')

        # 3. WHITELIST (IPs Amigos que nunca são banidos)
        WHITELISTED_IPS = [
            '127.0.0.1', 'localhost', 
            '172.16.10.1',   # OPNsense LAN
            '192.168.1.177', # Seu IP Windows
            '172.18.0.1','172.18.0.5', '172.18.0.7', '172.19.0.1', # Gateway Docker
            '172.16.10.101',
        ]
        
        if ip_address in WHITELISTED_IPS:
            return self.get_response(request)

        # 4. Verificação de Blacklist (IP e Rede)
        if BlockedIP.objects.filter(ip_address=ip_address).exists():
            blacklist_logger.warning(f"BLOQUEADO: IP na blacklist: {ip_address}")
            return HttpResponseForbidden('<h1>Acesso bloqueado permanentemente.</h1>')

        try:
            # CORREÇÃO AQUI: Usamos 'ip_address', e não 'ip_address_str'
            client_ip_obj = ipaddress.ip_address(ip_address)
            
            is_in_blocked_network = BlockedNetwork.objects.extra(
                where=["network::inet >>= %s::inet"], 
                params=[str(client_ip_obj)]
            ).exists()

            if is_in_blocked_network:
                blacklist_logger.warning(f"BLOQUEADO: Rede na blacklist: {ip_address}")
                return HttpResponseForbidden('<h1>Acesso bloqueado permanentemente (Rede).</h1>')
        except ValueError:
             pass 

        # 5. Rate Limit (apenas para URLs específicas)
        apply_rate_limit_paths = ['/search/', '/dashboard/', '/'] 
        should_apply_limit = False
        for path in apply_rate_limit_paths:
            if path in request.path:
                should_apply_limit = True
                break

        if not should_apply_limit:
            return self.get_response(request)

        # Lógica de contagem
        LIMIT = 120 
        PERIOD = 60
        request_log = cache.get(ip_address, [])
        current_time = time.time()
        valid_requests = [t for t in request_log if current_time - t < PERIOD]

        if len(valid_requests) >= LIMIT:
            BlockedIP.objects.get_or_create(ip_address=ip_address)
            cache.delete(ip_address)
            blacklist_logger.warning(f"RATE LIMIT EXCEDIDO: {ip_address} banido.")
            return HttpResponseForbidden('<h1>Seu IP foi adicionado à blacklist por atividade suspeita.</h1>')
        
        valid_requests.append(current_time)
        cache.set(ip_address, valid_requests, timeout=PERIOD)

        return self.get_response(request)

    def _get_client_ip(self, request):
        # 1. tenta pegar o IP real da Cloudflare (Prioridade Maxima)
        cf_ip = request.META.get('HTTP_CF_CONNECTING_IP')
        if cf_ip:
            return cf_ip

        # 2. Tenta pegar do X-Forwarded-For (Nginx/Ngrok)
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()

        # 3. Fallback para o endereço remoto direto
        return request.META.get('REMOTE_ADDR')
        