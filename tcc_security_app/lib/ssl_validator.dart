import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'dart:io';
import 'package:crypto/crypto.dart'; // Necessário para calcular o Hash

class SSLValidatorPage extends StatefulWidget {
  final String baseUrl; // URL do seu servidor Django (para consultar o oráculo)
  final String token;

  const SSLValidatorPage({super.key, required this.baseUrl, required this.token});

  @override
  State<SSLValidatorPage> createState() => _SSLValidatorPageState();
}

class _SSLValidatorPageState extends State<SSLValidatorPage> {
  final _urlController = TextEditingController();
  bool _isLoading = false;
  String _resultMessage = "";
  Color _resultColor = Colors.black;

  // Função principal de validação
  Future<void> _validateConnection() async {
    setState(() {
      _isLoading = true;
      _resultMessage = "Iniciando análise...";
      _resultColor = Colors.black;
    });

    String targetUrl = _urlController.text.trim();
    if (targetUrl.isEmpty) {
      setState(() {
        _isLoading = false;
        _resultMessage = "Por favor, digite uma URL.";
      });
      return;
    }

    // Remove http/https para pegar só o domínio
    String hostname = targetUrl.replaceAll(RegExp(r'^https?://'), '').split('/')[0];

    try {
      // 1. Pega o certificado LOCAL (como o celular vê o site)
      setState(() { _resultMessage = "Obtendo certificado local..."; });
      
      // Conecta na porta 443 (HTTPS)
      SecureSocket socket = await SecureSocket.connect(hostname, 443, onBadCertificate: (_) => true);
      
      // Extrai o certificado
      X509Certificate? cert = socket.peerCertificate;
      socket.destroy(); // Fecha conexão

      if (cert == null) throw Exception("Não foi possível obter o certificado do site.");

      // Calcula o Hash SHA-256 (Fingerprint)
      var bytes = cert.der;
      var digest = sha256.convert(bytes);
      
      // Formata como AA:BB:CC...
      String localFingerprint = digest.toString().toUpperCase();
      localFingerprint = localFingerprint.replaceAllMapped(RegExp(r".{2}"), (match) => "${match.group(0)}:");
      localFingerprint = localFingerprint.substring(0, localFingerprint.length - 1);

      // 2. Pergunta ao SERVIDOR (Django) qual é o Hash real
      setState(() { _resultMessage = "Consultando servidor de segurança..."; });
      
      final response = await http.post(
        Uri.parse('${widget.baseUrl}/accounts/api/ssl-check/'),
        headers: {
          'Authorization': 'Token ${widget.token}',
          'Content-Type': 'application/json; charset=UTF-8', // Cabeçalho JSON
        },
        body: jsonEncode({'target_url': hostname}), // <<< AQUI O jsonEncode É OBRIGATÓRIO
      );
      
      if (response.statusCode != 200) {
        throw Exception("Erro no servidor: ${response.statusCode}");
      }

      final serverData = jsonDecode(response.body);
      if (serverData['status'] == 'error') {
        throw Exception("Erro remoto: ${serverData['message']}");
      }

      String remoteFingerprint = serverData['fingerprint'];
      String issuer = serverData['issuer'];

      // 3. COMPARAÇÃO
      if (localFingerprint == remoteFingerprint) {
        setState(() { 
          _resultColor = Colors.green;
          _resultMessage = "✅ CONEXÃO SEGURA!\n\nDomínio: $hostname\nEmissor: $issuer\n\nO certificado que você vê é idêntico ao que o servidor de segurança vê.\nNenhum interceptador detectado."; 
        });
      } else {
         setState(() { 
            _resultColor = Colors.red;
            _resultMessage = "🚨 PERIGO: INTERCEPTAÇÃO DETECTADA!\n\nDomínio: $hostname\n\nHash Local (Você vê):\n$localFingerprint\n\nHash Real (Servidor vê):\n$remoteFingerprint\n\nAlguém está interceptando sua conexão (Ataque MitM)!"; 
        });
      }

    } catch (e) {
      setState(() { 
        _resultColor = Colors.orange;
        _resultMessage = "Erro na validação: $e"; 
      });
    } finally {
      setState(() { _isLoading = false; });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Validador SSL Anti-MitM")),
      body: Padding(
        padding: const EdgeInsets.all(20.0),
        child: SingleChildScrollView(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              const Icon(Icons.lock_outline, size: 80, color: Colors.blueGrey),
              const SizedBox(height: 20),
              const Text(
                "Verifique se a conexão com um site é segura ou se está sendo interceptada.",
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 30),
              
              TextField(
                controller: _urlController,
                decoration: const InputDecoration(
                  labelText: 'Digite o site (ex: google.com)',
                  border: OutlineInputBorder(),
                  prefixIcon: Icon(Icons.link),
                ),
              ),
              const SizedBox(height: 20),
              
              SizedBox(
                height: 50,
                child: ElevatedButton(
                  onPressed: _isLoading ? null : _validateConnection,
                  style: ElevatedButton.styleFrom(backgroundColor: Colors.blueGrey, foregroundColor: Colors.white),
                  child: _isLoading 
                    ? const CircularProgressIndicator(color: Colors.white)
                    : const Text("VALIDAR CONEXÃO"),
                ),
              ),
              
              const SizedBox(height: 30),
              
              Container(
                padding: const EdgeInsets.all(15),
                decoration: BoxDecoration(
                  color: _resultColor.withOpacity(0.1),
                  border: Border.all(color: _resultColor.withOpacity(0.5)),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Text(
                  _resultMessage,
                  style: TextStyle(color: _resultColor, fontWeight: FontWeight.bold),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}