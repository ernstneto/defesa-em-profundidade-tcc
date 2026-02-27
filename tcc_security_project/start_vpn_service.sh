#!/bin/bash

# Caminho para salvar o endereço (dentro da pasta do projeto para o Docker ver)
OUTPUT_FILE="./current_vpn.txt"

echo "--- 🚀 Iniciando Serviço de VPN Dinâmica (TCC) ---"

# 1. Limpeza
pkill -f "ssh -p 443 -R0"

# 2. Iniciar o Túnel (Pinggy TCP)
# Aponta para o pfSense (172.16.10.1:1194)
echo "📡 Conectando ao Pinggy..."
nohup ssh -o StrictHostKeyChecking=no -p 443 -R0:172.16.10.1:1194 tcp@a.pinggy.io > vpn.log 2>&1 &

# 3. Aguardar e Capturar
echo "⏳ Aguardando endereço..."
sleep 8

# Captura a URL do log (formato tcp://...)
VPN_URL=$(grep -a -o "tcp://[^ ]*:[0-9]*" vpn.log | head -n 1)

if [ -z "$VPN_URL" ]; then
    echo "❌ ERRO: Falha ao obter endereço do túnel."
    echo "OFFLINE" > $OUTPUT_FILE
    exit 1
fi

# 4. Salvar para o Django
echo "$VPN_URL" > $OUTPUT_FILE

echo "✅ SUCESSO! VPN Disponível em: $VPN_URL"
echo "📂 Endereço salvo em $OUTPUT_FILE para o Django."