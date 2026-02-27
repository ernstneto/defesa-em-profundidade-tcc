import subprocess
import time
import re
import os

# --- CONFIGURAÇÕES ---
# Coloque aqui o caminho para seus certificados reais
CA_CERT_PATH = "/etc/openvpn/server/ca.crt"  # Ajuste conforme necessário
CLIENT_CERT_PATH = "/etc/openvpn/client/client.crt" # Gere um certificado para cliente
CLIENT_KEY_PATH = "/etc/openvpn/client/client.key"

# Nome do arquivo de saída
OUTPUT_OVPN = "ForensicVault_Client.ovpn"

# Template do arquivo OVPN
# Observe os placeholders {{REMOTE_HOST}} e {{REMOTE_PORT}}
OVPN_TEMPLATE = """client
dev tun
proto tcp
remote {{REMOTE_HOST}} {{REMOTE_PORT}}
resolv-retry infinite
nobind
persist-key
persist-tun

# --- TIPO DE CONEXÃO (COMENTE/DESCOMENTE ABAIXO) ---
# Opção 1: Full Tunnel (Todo tráfego passa pela VPN - Mais Seguro)
redirect-gateway def1

# Opção 2: Split Tunnel (Apenas acesso à LAN 172.16.10.x passa pela VPN)
# Para usar esta, comente a linha 'redirect-gateway' acima e descomente abaixo:
# route 172.16.10.0 255.255.255.0

# --- AUTENTICAÇÃO ---
# Exige Login e Senha
auth-user-pass
remote-cert-tls server
cipher AES-256-GCM
auth SHA256
verb 3

<ca>
{{CA_CONTENT}}
</ca>

<cert>
{{CERT_CONTENT}}
</cert>

<key>
{{KEY_CONTENT}}
</key>
"""

def read_file(path):
    try:
        with open(path, 'r') as f:
            return f.read().strip()
    except FileNotFoundError:
        return "ERRO: Arquivo não encontrado"

def start_pinggy():
    print("[*] Iniciando túnel Pinggy...")
    # Inicia o SSH em background e redireciona a saída para um arquivo temporário
    # Ajuste o comando ssh conforme seu comando original (ex: ssh -p 443 -R0:localhost:1194 a.pinggy.io)
    # Aqui assumimos que o OpenVPN roda na 1194 TCP localmente
    cmd = "ssh -o StrictHostKeyChecking=no -R0:localhost:1194 tcp@a.pinggy.io"
    
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    return process

def generate_ovpn(host, port):
    print(f"[*] Gerando arquivo {OUTPUT_OVPN} para {host}:{port}...")
    
    ca = read_file(CA_CERT_PATH)
    cert = read_file(CLIENT_CERT_PATH)
    key = read_file(CLIENT_KEY_PATH)

    # Substitui os placeholders
    content = OVPN_TEMPLATE.replace("{{REMOTE_HOST}}", host)
    content = OVPN_TEMPLATE.replace("{{REMOTE_PORT}}", port)
    content = OVPN_TEMPLATE.replace("{{CA_CONTENT}}", ca)
    content = OVPN_TEMPLATE.replace("{{CERT_CONTENT}}", cert)
    content = OVPN_TEMPLATE.replace("{{KEY_CONTENT}}", key)

    with open(OUTPUT_OVPN, 'w') as f:
        f.write(content)
    
    print(f"[SUCCESS] Arquivo gerado: {os.path.abspath(OUTPUT_OVPN)}")
    print("Envie este arquivo para seu celular ou cliente Windows.")

def main():
    process = start_pinggy()
    
    print("[*] Aguardando conexão Pinggy estabelecer...")
    
    # Pinggy geralmente imprime algo como: "tcp://t.pinggy.io:12345"
    found = False
    buffer = ""
    
    try:
        # Loop para ler a saída do SSH linha por linha até achar a URL
        while True:
            char = process.stdout.read(1)
            if not char:
                break
            buffer += char
            if "\n" in buffer:
                line = buffer.strip()
                # Procura padrão tcp://...
                match = re.search(r"tcp://([^:]+):(\d+)", line)
                if match:
                    host = match.group(1)
                    port = match.group(2)
                    print(f"[*] Túnel detectado: {host}:{port}")
                    generate_ovpn(host, port)
                    found = True
                    break # Sai do loop de leitura, mas mantem o processo rodando
                buffer = ""
        
        if found:
            print("[*] O túnel está ATIVO. Pressione Ctrl+C para encerrar a VPN.")
            process.wait() # Mantém o script rodando para segurar o túnel
            
    except KeyboardInterrupt:
        print("\n[*] Encerrando túnel...")
        process.terminate()

if __name__ == "__main__":
    main()