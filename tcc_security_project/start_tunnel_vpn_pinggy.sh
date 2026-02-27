#!/bin/bash

# --- CONFIGURAÇÃO DO GITHUB ---
#GITHUB_TOKEN=""
GITHUB_USER="ernstneto"
GITHUB_REPO="TCC_ACCESS"
GITHUB_FILE="vpn_link.txt"

echo "--- Iniciando Automação da VPN (Pinggy TCP) ---"

# 1. Limpeza (Mata processos SSH do Pinggy antigos)
pkill -f "ssh -p 443 -R0"

# 2. Iniciar Pinggy TCP
# Aponta para o IP do pfSense (172.16.10.1) na porta 1194
# -o StrictHostKeyChecking=no: Evita travar pedindo "yes"
echo "Conectando ao Pinggy..."
nohup ssh -o StrictHostKeyChecking=no -p 443 -R0:172.16.10.1:1194 tcp@a.pinggy.io > pinggy.log 2>&1 &

echo "Aguardando túnel (10s)..."
sleep 10

# 3. Capturar URL do log
# O Pinggy mostra algo como "tcp://r.pinggy.io:12345"
VPN_URL=$(grep -a -o "tcp://[^ ]*:[0-9]*" pinggy.log | head -n 1)

if [ -z "$VPN_URL" ]; then
    echo "ERRO: Não foi possível capturar a URL. Veja o log:"
    cat pinggy.log
    exit 1
fi

echo ">>> VPN ATIVA EM: $VPN_URL <<<"

# 4. ATUALIZAR ARQUIVO LOCAL (Para o Django injetar no download)
echo $VPN_URL > current_vpn.txt
echo "Arquivo local 'current_vpn.txt' atualizado."

# 5. ATUALIZAR GITHUB
echo "Atualizando GitHub..."
CONTENT_BASE64=$(echo -n "$VPN_URL" | base64)
FILE_SHA=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
    "https://api.github.com/repos/$GITHUB_USER/$GITHUB_REPO/contents/$GITHUB_FILE" | jq -r .sha)

if [ -z "$FILE_SHA" ] || [ "$FILE_SHA" == "null" ]; then
    JSON_DATA=$(printf '{"message":"Novo link VPN Pinggy","content":"%s"}' "$CONTENT_BASE64")
else
    JSON_DATA=$(printf '{"message":"Update link VPN Pinggy","content":"%s","sha":"%s"}' "$CONTENT_BASE64" "$FILE_SHA")
fi

curl -s -o /dev/null -X PUT -H "Authorization: token $GITHUB_TOKEN" \
    -d "$JSON_DATA" \
    "https://api.github.com/repos/$GITHUB_USER/$GITHUB_REPO/contents/$GITHUB_FILE"

echo "✅ GitHub atualizado com sucesso!"
echo "Link: https://github.com/$GITHUB_USER/$GITHUB_REPO/blob/main/$GITHUB_FILE"
