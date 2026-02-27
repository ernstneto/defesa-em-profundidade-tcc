import requests
import sys
import os
from requests.packages.urllib3.exceptions import InsecureRequestWarning

# Desabilita avisos de SSL inseguro (para limpar a tela)
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# --- CONFIGURAÇÃO ---
# Se o seu servidor tiver um domínio, coloque aqui. Se for IP, mantenha.
URL_ALVO = "https://172.16.10.101:8000/accounts/login/" 

# Proxy do Burp (Endereço padrão). 
# Se a vítima estiver em outra máquina, mude 127.0.0.1 para o IP do Kali.
PROXY_IP = "127.0.0.1" 
PROXY_PORT = "8080"

def limpar_tela():
    os.system('cls' if os.name == 'nt' else 'clear')

def verificar_seguranca():
    limpar_tela()
    print("="*60)
    print(f"    FERRAMENTA DE AUDITORIA DE INTEGRIDADE SSL - TCC")
    print("="*60)
    print(f"[*] Alvo: {URL_ALVO}")
    
    # Pergunta se quer testar COM ou SEM proxy
    print("\nEscolha o modo de teste:")
    print("1 - Teste Direto (Verificar se o site está acessível)")
    print("2 - Simular Ataque (Passar pelo Proxy BurpSuite/MitM)")
    opcao = input("\nDigite a opção (1 ou 2): ")

    proxies = None
    if opcao == '2':
        proxies = {
            "https": f"http://{PROXY_IP}:{PROXY_PORT}",
            "http": f"http://{PROXY_IP}:{PROXY_PORT}"
        }
        print(f"\n[*] ATENÇÃO: Redirecionando tráfego via Proxy {PROXY_IP}:{PROXY_PORT}...")
    else:
        print("\n[*] Iniciando conexão direta...")

    print("-" * 60)

    try:
        # Tenta conectar validando o certificado (verify=True)
        response = requests.get(URL_ALVO, proxies=proxies, verify=True, timeout=10)
        
        print("\n[PERIGO] CONEXÃO ACEITA! (FALHA DE SEGURANÇA)")
        print("Motivo: O cliente confiou no certificado apresentado.")
        print(f"Status Code: {response.status_code}")
        print("Se você está sob ataque, isso significa que seu dispositivo foi comprometido.")
        
    except requests.exceptions.SSLError as e:
        print("\n[SUCESSO] ATAQUE BLOQUEADO! (SEGURANÇA ATIVA)")
        print("Motivo: O certificado foi rejeitado por não ser confiável.")
        print("A ferramenta detectou uma tentativa de interceptação (MitM).")
        print(f"\nDetalhe Técnico: {e}")
        
    except Exception as e:
        print(f"\n[ERRO DE CONEXÃO] Não foi possível alcançar o servidor.")
        print(f"Detalhe: {e}")

    print("-" * 60)
    input("\nPressione ENTER para fechar a ferramenta...")

if __name__ == "__main__":
    verificar_seguranca()