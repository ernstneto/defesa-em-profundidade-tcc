import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'dashboard.dart'; // Importa a nova tela

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'TCC Security',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.blueGrey),
        useMaterial3: true,
      ),
      home: const LoginPage(),
    );
  }
}

class LoginPage extends StatefulWidget {
  const LoginPage({super.key});

  @override
  State<LoginPage> createState() => _LoginPageState();
}

class _LoginPageState extends State<LoginPage> {
  final String githubRawUrl = "https://raw.githubusercontent.com/ernstneto/TCC_ACCESS/main/access_link.txt";
  
  String _baseUrl = "";
  // Status: 0=Buscando, 1=Online(Verde), 2=Offline(Vermelho)
  int _serverStatus = 0; 
  String _statusMessage = "Iniciando...";

  final _usernameController = TextEditingController();
  final _passwordController = TextEditingController();
  bool _isLoginLoading = false;

  @override
  void initState() {
    super.initState();
    _fetchAndCheckServer();
  }

  // 1. Busca URL no GitHub e 2. Testa se está Online
  Future<void> _fetchAndCheckServer() async {
    setState(() { _serverStatus = 0; _statusMessage = "Buscando satélite..."; });

    try {
      // Passo 1: Pegar a URL
      final uri = Uri.parse('$githubRawUrl?t=${DateTime.now().millisecondsSinceEpoch}');
      final responseGithub = await http.get(uri);

      if (responseGithub.statusCode == 200) {
        final url = responseGithub.body.trim();
        _baseUrl = url;

        // Passo 2: Teste de Conectividade (Ping no Servidor)
        setState(() { _statusMessage = "Testando conexão com $url..."; });
        
        try {
          // Tenta acessar o login para ver se responde 200 OK
          print("Testando conexão com: $url/accounts/login/"); // Log no console
          final responsePing = await http.get(Uri.parse('$url/accounts/login/')).timeout(const Duration(seconds: 10));
          
          print("Status Code recebido: ${responsePing.statusCode}"); // Log essencial
          
          if (responsePing.statusCode == 200) {
            setState(() {
              _serverStatus = 1; 
              _statusMessage = "Servidor ONLINE e Seguro";
            });
          } else {
            // MOSTRA O ERRO NA TELA
            setState(() {
              _serverStatus = 2; 
              _statusMessage = "Erro ${responsePing.statusCode}: Recusado pelo servidor";
            });
          }
        } catch (e) {
          print("Erro de exceção: $e");
          setState(() {
            _serverStatus = 2; 
            _statusMessage = "Erro de Rede: $e";
          });
        }
        
      } else {
        setState(() { _serverStatus = 2; _statusMessage = "Erro no GitHub"; });
      }
    } catch (e) {
      setState(() { _serverStatus = 2; _statusMessage = "Sem Internet"; });
    }
  }

  Future<void> _login() async {
    if (_serverStatus != 1) return; // Só loga se estiver verde

    setState(() { _isLoginLoading = true; });

    try {
      final response = await http.post(
        Uri.parse('$_baseUrl/accounts/api/login/'),
        body: {
          'username': _usernameController.text,
          'password': _passwordController.text,
        },
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        final token = data['token'];
        
        // SUCESSO: Navega para o Dashboard passando o Token
        if (!mounted) return;
        Navigator.push(
          context,
          MaterialPageRoute(
            builder: (context) => DashboardPage(token: token, baseUrl: _baseUrl),
          ),
        );
      } else {
        if (!mounted) return;
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Credenciais Inválidas!'), backgroundColor: Colors.red),
        );
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Erro: $e')),
      );
    } finally {
      setState(() { _isLoginLoading = false; });
    }
  }

  @override
  Widget build(BuildContext context) {
    // Define a cor e ícone baseado no status
    Color statusColor;
    IconData statusIcon;
    if (_serverStatus == 1) {
      statusColor = Colors.green;
      statusIcon = Icons.check_circle;
    } else if (_serverStatus == 2) {
      statusColor = Colors.red;
      statusIcon = Icons.error;
    } else {
      statusColor = Colors.orange;
      statusIcon = Icons.sync;
    }

    return Scaffold(
      body: Center(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Icon(Icons.security, size: 80, color: Colors.blueGrey),
              const SizedBox(height: 20),
              const Text("TCC Security Access", style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold)),
              const SizedBox(height: 40),

              // --- STATUS DO SERVIDOR ---
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: statusColor.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: statusColor),
                ),
                child: Row(
                  children: [
                    Icon(statusIcon, color: statusColor, size: 30),
                    const SizedBox(width: 15),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            _serverStatus == 1 ? "SISTEMA OPERACIONAL" : "SISTEMA OFF-LINE",
                            style: TextStyle(color: statusColor, fontWeight: FontWeight.bold),
                          ),
                          Text(_statusMessage, style: const TextStyle(fontSize: 12)),
                        ],
                      ),
                    ),
                    if (_serverStatus != 1)
                      IconButton(
                        icon: const Icon(Icons.refresh),
                        onPressed: _fetchAndCheckServer,
                      )
                  ],
                ),
              ),
              const SizedBox(height: 30),

              TextField(
                controller: _usernameController,
                decoration: const InputDecoration(
                  labelText: 'Usuário',
                  prefixIcon: Icon(Icons.person_outline),
                  border: OutlineInputBorder(),
                ),
              ),
              const SizedBox(height: 15),
              TextField(
                controller: _passwordController,
                obscureText: true,
                decoration: const InputDecoration(
                  labelText: 'Senha',
                  prefixIcon: Icon(Icons.lock_outline),
                  border: OutlineInputBorder(),
                ),
              ),
              const SizedBox(height: 30),

              SizedBox(
                width: double.infinity,
                height: 50,
                child: ElevatedButton(
                  onPressed: _serverStatus == 1 && !_isLoginLoading ? _login : null,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.blueGrey,
                    foregroundColor: Colors.white,
                    disabledBackgroundColor: Colors.grey[300],
                  ),
                  child: _isLoginLoading
                      ? const SizedBox(width: 24, height: 24, child: CircularProgressIndicator(color: Colors.white))
                      : const Text("ENTRAR", style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}