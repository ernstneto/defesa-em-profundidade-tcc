#!/bin/bash

# --- CONFIGURAÇÃO ---
#GITHUB_TOKEN=""
GITHUB_USER="ernstneto"
GITHUB_REPO="TCC_ACCESS"
GITHUB_FILE="access_link_ngrok.txt"

echo "--- Iniciando Automação do Túnel Ngrok ---"

# 1. Limpeza
pkill -x ngrok

# 2. Identificar onde está o ngrok
if [ -f "./ngrok" ]; then
    NGROK_CMD="./ngrok"
    echo "Usando ngrok local (./ngrok)"
else
    NGROK_CMD="ngrok"
    echo "Usando ngrok do sistema (global)"
fi

# 3. Iniciar Ngrok
# O segredo: Redirecionar stdout E stderr para o arquivo de log
nohup $NGROK_CMD http 8000 > ngrok.log 2>&1 &

echo "Aguardando o túnel subir (10s)..."
sleep 10

# Verifica se morreu
if ! pgrep -x "ngrok" > /dev/null; then
    echo "ERRO CRÍTICO: O ngrok não iniciou."
    echo "--- LOG ---"
    cat ngrok.log
    exit 1
fi

# 4. Capturar URL via API (jq é obrigatório para precisão)
# Se não tiver jq, tenta instalar ou usa grep tosco
if ! command -v jq &> /dev/null; then
    echo "Aviso: 'jq' não instalado. Tentando usar grep (menos confiável)..."
    NGROK_URL=$(curl -s http://127.0.0.1:4040/api/tunnels | grep -o "https://[a-z0-9-]*\.ngrok-free\.app" | head -n 1)
else
    NGROK_URL=$(curl -s http://127.0.0.1:4040/api/tunnels | jq -r '.tunnels[0].public_url')
fi

if [ -z "$NGROK_URL" ] || [ "$NGROK_URL" == "null" ]; then
    echo "ERRO: Falha ao obter URL. API do Ngrok:"
    curl -s http://127.0.0.1:4040/api/tunnels
    exit 1
fi

echo ">>> TÚNEL ATIVO EM: $NGROK_URL <<<"

# 5. Atualizar Django (ESSENCIAL PARA FUNCIONAR)
echo "Atualizando banco de dados do Django..."
CLEAN_DOMAIN=$(echo $NGROK_URL | sed 's/https:\/\///')
docker compose exec -T web python manage.py update_domain $CLEAN_DOMAIN

# 6. Salvar localmente
echo $NGROK_URL > current_url_ngrok.txt

# 7. Atualizar GitHub
echo "Atualizando GitHub..."
CONTENT_BASE64=$(echo -n "$NGROK_URL" | base64)
FILE_SHA=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
    "https://api.github.com/repos/$GITHUB_USER/$GITHUB_REPO/contents/$GITHUB_FILE" | jq -r .sha)

if [ "$FILE_SHA" = "null" ] || [ -z "$FILE_SHA" ]; then
    JSON_DATA=$(jq -n --arg c "$CONTENT_BASE64" '{message:"Novo link",content:$c}')
else
    JSON_DATA=$(jq -n --arg c "$CONTENT_BASE64" --arg s "$FILE_SHA" '{message:"Update link",content:$c,sha:$s}')
fi

curl -s -o /dev/null -X PUT -H "Authorization: token $GITHUB_TOKEN" \
    -d "$JSON_DATA" \
    "https://api.github.com/repos/$GITHUB_USER/$GITHUB_REPO/contents/$GITHUB_FILE"

echo "✅ Sucesso! GitHub atualizado."