import requests
import sys

# URL do seu site (ajuste conforme necessário)
URL_ALVO = "https://172.16.10.101:8000"  # Ou o domínio se tiver DNS
# Proxy do Burp Suite (para forçar o tráfego a passar por ele)
PROXIES = {
    "http": "http://127.0.0.1:8080",
    "https": "http://127.0.0.1:8080",
}

print(f"[*] Iniciando teste de conexão segura para: {URL_ALVO}")
print(f"[*] Usando Proxy: {PROXIES['https']}")
print("-" * 50)

try:
    # O parâmetro verify=True (padrão) obriga a checagem do certificado
    response = requests.get(URL_ALVO, proxies=PROXIES, verify=True, timeout=5)
    
    print("[SUCESSO] Conexão estabelecida!")
    print(f"Status Code: {response.status_code}")
    print("Isso significa que o cliente CONFIA no certificado apresentado.")

except requests.exceptions.SSLError as e:
    print("[ERRO DE SEGURANÇA DETECTADO]")
    print("A conexão foi abortada porque o certificado é inválido ou desconhecido.")
    print("-" * 50)
    print(f"Detalhe do erro: {e}")
    print("-" * 50)
    print("CONCLUSÃO: O ataque Man-in-the-Middle foi bloqueado pelo cliente.")

except Exception as e:
    print(f"[ERRO GERAL] Ocorreu um erro não relacionado ao SSL: {e}")