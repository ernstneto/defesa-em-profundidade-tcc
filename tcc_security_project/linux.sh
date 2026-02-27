#!/bin/bash

# Variáveis
VPN_SERVER_IP="192.168.1.200"
VPN_PORT="1194"
LOCAL_SUBNET="192.168.1.0/24"
OVPN_FILE="cliente.ovpn"

echo "[+] Iniciando configuração de Endpoint Seguro..."

# 1. Instalar Dependências
apt-get update
apt-get install -y openvpn ufw resolvconf openvpn-systemd-resolved

# 2. Configurar Firewall (Kill Switch)
echo "[+] Configurando Kill Switch (UFW)..."
ufw --force reset
ufw default deny incoming
ufw default deny outgoing

# Permissões Essenciais
ufw allow out to $LOCAL_SUBNET comment 'Rede Local'
ufw allow in from $LOCAL_SUBNET comment 'Rede Local'
ufw allow out on tun0 comment 'Tunel VPN'
ufw allow in on tun0 comment 'Tunel VPN'
ufw allow out to $VPN_SERVER_IP port $VPN_PORT proto udp comment 'Conexao VPN'

# Ativar
ufw --force enable

# 3. Conectar (Opcional: criar um serviço systemd para conectar no boot)
echo "[+] Conectando à VPN..."
openvpn --config $OVPN_FILE --daemon

echo "[SUCCESS] Ambiente Seguro Ativado!"