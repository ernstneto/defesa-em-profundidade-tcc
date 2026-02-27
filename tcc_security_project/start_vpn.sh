#!/bin/bash

echo "--- Iniciando VPN Dinâmica (Pinggy) ---"

# 1. Matar processos anteriores
pkill -f "ssh -p 443 -R0"

# 2. Iniciar o Túnel
# Redireciona a saída para um arquivo para podermos ler
# O pfSense está em 172.16.10.1:1194 (Lembre de configurar o OpenVPN para TCP no pfSense!)
echo "Conectando ao Pinggy..."
nohup ssh -p 443 -R0:172.16.10.1:1194 tcp@a.pinggy.io > vpn_tunnel.log 2>&1 &

# 3. Aguardar e Capturar URL
echo "Aguardando URL (5s)..."
sleep 5

# O Pinggy joga a URL no log. Vamos pescar ela.
# Procura por "tcp://"
VPN_URL=$(grep -o "tcp://[^ ]*" vpn_tunnel.log | head -1)

if [ -z "$VPN_URL" ]; then
    echo "ERRO: Não foi possível capturar a URL. Veja o log:"
    cat vpn_tunnel.log
    exit 1
fi

echo ">>> VPN ATIVA EM: $VPN_URL <<<"

# 4. Salvar para o Django ler
# Salva no volume do Django (pasta atual mapeada para /app)
echo $VPN_URL > current_vpn.txt
echo "Endereço atualizado em current_vpn.txt"

# (Opcional) Atualizar GitHub também, se quiser
# ... (código do GitHub igual ao do site) ...