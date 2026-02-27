#!/bin/bash

# --- CONFIGURACAO DO GITHUB ---
#GITHUB_TOKEN=""
GITHUB_USER="ernstneto"
GITHUB_REPO="TCC_ACCESS"
GITHUB_FILE="access_link.txt"

echo "--- Iniciando Automação do Túnel TCC ---"

# 1. Matar túneis antigos
echo "Encerrando túneis antigos..."
pkill -f cloudflared
sleep 2

# 2. Iniciar o Cloudflare Tunnel (MÉTODO ANTIGO - ainda funciona)
echo "Iniciando cloudflared..."
nohup cloudflared tunnel --url http://localhost:8000 > tunnel.log 2>&1 &

echo "Aguardando URL..."
sleep 10  # Aumente o tempo para 10 segundos

# 3. CAPTURA DA URL ATUALIZADA (MUDANÇA PRINCIPAL)
# Tenta o NOVO padrão primeiro (FL2 - mais recente)
echo "Capturando URL do túnel..."
TUNNEL_URL=$(grep -a -o 'https://[-a-z0-9]*\.cfargotunnel\.com' tunnel.log | head -1)

# Se não encontrar, tenta o padrão antigo como fallback
if [ -z "$TUNNEL_URL" ]; then
    TUNNEL_URL=$(grep -a -o 'https://[-a-z0-9]*\.trycloudflare\.com' tunnel.log | head -1)
fi

# Método alternativo: verificar conexões ativas
if [ -z "$TUNNEL_URL" ]; then
    echo "Tentando método alternativo..."
    TUNNEL_URL=$(ss -tulpn | grep cloudflared | grep -o 'cfargotunnel[^ ]*' | head -1)
    if [ ! -z "$TUNNEL_URL" ]; then
        TUNNEL_URL="https://$TUNNEL_URL"
    fi
fi

if [ -z "$TUNNEL_URL" ]; then
    echo "ERRO: Não foi possível capturar a URL."
    echo "Verificando logs..."
    tail -20 tunnel.log
    echo "Tente executar manualmente: cloudflared tunnel --url http://localhost:8000"
    exit 1
fi

echo ">>> TÚNEL ATIVO EM: $TUNNEL_URL <<<"

# 4. Atualizar o Django (REAPROVEITADO)
CLEAN_DOMAIN=$(echo $TUNNEL_URL | sed 's|https://||')
docker-compose exec -T web python manage.py update_domain "$CLEAN_DOMAIN"

# 5. Salvar localmente (REAPROVEITADO)
echo $TUNNEL_URL > current_url.txt

# --- 6. ATUALIZAR O GITHUB (REAPROVEITADO) ---
echo "Atualizando GitHub..."
CONTENT_BASE64=$(echo -n "$TUNNEL_URL" | base64 -w 0)

FILE_SHA=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
    "https://api.github.com/repos/$GITHUB_USER/$GITHUB_REPO/contents/$GITHUB_FILE" | jq -r .sha)

if [ "$FILE_SHA" = "null" ]; then
    JSON_DATA=$(jq -n --arg content "$CONTENT_BASE64" \
        '{message: "Criando link de acesso", content: $content}')
else
    JSON_DATA=$(jq -n --arg content "$CONTENT_BASE64" --arg sha "$FILE_SHA" \
        '{message: "Atualizando link de acesso", content: $content, sha: $sha}')
fi

RESPONSE=$(curl -s -X PUT -H "Authorization: token $GITHUB_TOKEN" \
    -H "Content-Type: application/json" \
    -d "$JSON_DATA" \
    "https://api.github.com/repos/$GITHUB_USER/$GITHUB_REPO/contents/$GITHUB_FILE")

echo "GitHub atualizado! Veja em: https://github.com/$GITHUB_USER/$GITHUB_REPO/blob/main/$GITHUB_FILE"
echo "--- Pronto! Pode acessar: $TUNNEL_URL ---"