# accounts/signals.py

import requests
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from django.contrib import messages
from .models import LoginHistory

@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    # --- DEBUGGING DETALHADO ---
    print(f"--- LOGIN DETECTADO ---")
    print(f"Usuário: {user.username}")
    remote_addr = request.META.get('REMOTE_ADDR')
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    x_real_ip = request.META.get('HTTP_X_REAL_IP')
    print(f"DEBUG: request.META.get('REMOTE_ADDR') = {remote_addr}")
    print(f"DEBUG: request.META.get('HTTP_X_FORWARDED_FOR') = {x_forwarded_for}")
    print(f"DEBUG: request.META.get('HTTP_X_REAL_IP') = {x_real_ip}")

    # Lógica para determinar o IP real (funciona bem com Nginx e Ngrok)
    if x_forwarded_for:
        # Pega o primeiro IP da lista X-Forwarded-For (o IP original do cliente)
        client_ip_real = x_forwarded_for.split(',')[0].strip()
    else:
        # Fallback para o IP que conectou diretamente (deve ser o Ngrok ou Nginx)
        client_ip_real = remote_addr

    print(f"IP (real) do Cliente Determinado: {client_ip_real}")
    
    # --- BLOCO DE SIMULAÇÃO (Comentado, pois Ngrok deve fornecer IPs públicos reais) ---
    # KALI_VPN_IP_PRIVADO = '192.168.1.120' # Ajuste se necessário
    # client_ip_para_api = client_ip_real # Por padrão, usa o IP real
    # if client_ip_real == KALI_VPN_IP_PRIVADO:
    #     client_ip_para_api = '8.8.8.8' # Simula EUA
    #     print(f"!!! SIMULAÇÃO ATIVA: Usando IP {client_ip_para_api} para API.")
    # elif client_ip_real.startswith(('192.168.', '172.', '10.')):
    #      client_ip_para_api = '177.135.195.130' # Simula Brasil
    #      print(f"!!! SIMULAÇÃO ATIVA: Usando IP {client_ip_para_api} para API.")
    # print(f"IP a ser enviado para API: {client_ip_para_api}")
    # --- FIM SIMULAÇÃO ---
    
    # Usa o IP real determinado para a API
    client_ip_para_api = client_ip_real

    current_country = None
    current_city = None

    # Usar a API para obter a geolocalização
    try:
        api_url = f"https://proxycheck.io/v2/{client_ip_para_api}?vpn=1&asn=1&tag=TCC_Login_Ngrok"
        response = requests.get(api_url, timeout=10) # Aumentei o timeout um pouco
        response.raise_for_status()
        api_data = response.json()

        print(f"Resposta da API proxycheck.io: {api_data}")

        if api_data.get('status') == 'ok':
            geo_info = api_data.get(client_ip_para_api, {})
            current_country = geo_info.get('country')
            current_city = geo_info.get('city')
        # Adiciona tratamento para erro da API (IP privado/inválido)
        elif api_data.get('status') == 'error' and 'private address' in api_data.get('message','').lower():
             print(f"API ignorou IP privado: {client_ip_para_api}")
             # Deixa country/city como None, o login continua mas sem GeoIP
        else:
            print(f"Erro da API proxycheck.io: {api_data.get('message', 'Resposta inválida')}")

    except requests.RequestException as e:
         print(f"Erro ao chamar API: {e}")
         # Falha na API não deve impedir o login

    # Lógica de Detecção de Anomalia
    known_countries = LoginHistory.objects.filter(user=user).exclude(country__isnull=True).values_list('country', flat=True).distinct()

    print(f"Países conhecidos (não nulos) para {user.username}: {list(known_countries)}")
    print(f"País atual detectado: {current_country}")

    is_new_country = current_country and current_country not in known_countries
    has_history = known_countries.exists() # Verifica se há histórico com país não nulo

    if is_new_country and has_history:
        messages.warning(request,
            f'ALERTA DE SEGURANÇA: Detectamos um novo login na sua conta a partir de um local incomum ({current_city}, {current_country}). '
            'Se não foi você, recomendamos que troque sua senha imediatamente.'
        )
        print(f"*** ALERTA DE NOVO PAÍS GERADO! ***")

    # Salvar o novo login no histórico (sempre salva o IP real)
    LoginHistory.objects.create(
        user=user,
        ip_address=client_ip_real, # Salva o IP real
        country=current_country,
        city=current_city
    )