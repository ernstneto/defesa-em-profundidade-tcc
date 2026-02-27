# Script de Hardening e Kill Switch para Windows
# Salvar como: setup_secure_vpn.ps1

# 1. Define variáveis
$VpnServerIP = "192.168.1.200" # IP da WAN do pfSense
$VpnPort = "1194"

# 2. Cria a regra de "Permitir VPN" (A única saída permitida)
New-NetFirewallRule -DisplayName "Permitir Conexao VPN TCC" `
    -Direction Outbound `
    -Action Allow `
    -Protocol UDP `
    -RemoteAddress $VpnServerIP `
    -RemotePort $VpnPort

# 3. Cria a regra de "Permitir TUNNEL" (A interface virtual do OpenVPN)
# Nota: O Windows identifica interfaces por perfis ou nomes.
# A automação aqui geralmente envolve permitir o executável do openvpn.exe
New-NetFirewallRule -DisplayName "Permitir Trafego OpenVPN" `
    -Direction Outbound `
    -Action Allow `
    -Program "C:\Program Files\OpenVPN\bin\openvpn.exe"

# 4. Bloqueia todo o resto (O Kill Switch)
# CUIDADO: Isso bloqueia a internet se as regras acima falharem
Set-NetFirewallProfile -Profile Domain,Public,Private -DefaultOutboundAction Block