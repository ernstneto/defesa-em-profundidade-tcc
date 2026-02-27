import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'ssl_validator.dart';

class DashboardPage extends StatefulWidget {
  final String token;
  final String baseUrl;

  const DashboardPage({super.key, required this.token, required this.baseUrl});

  @override
  State<DashboardPage> createState() => _DashboardPageState();
}

class _DashboardPageState extends State<DashboardPage> {
  Map<String, dynamic>? _userData;
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _fetchUserData();
  }

  // Busca os dados do usuário usando o Token
  Future<void> _fetchUserData() async {
    try {
      final response = await http.get(
        Uri.parse('${widget.baseUrl}/accounts/api/user/'), // Endpoint que criamos antes
        headers: {
          'Authorization': 'Token ${widget.token}', // O "Crachá" de acesso
        },
      );

      if (response.statusCode == 200) {
        setState(() {
          _userData = jsonDecode(response.body);
          _isLoading = false;
        });
      } else {
        // Se o token expirou ou é inválido
        Navigator.pop(context); // Volta para o login
        ScaffoldMessenger.of(context).showSnackBar(
           SnackBar(content: Text('Sessão expirada: ${response.statusCode}')),
        );
      }
    } catch (e) {
      setState(() { _isLoading = false; });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("Área Segura"),
        backgroundColor: Colors.green,
        foregroundColor: Colors.white,
        actions: [
          IconButton(
            icon: const Icon(Icons.logout),
            onPressed: () => Navigator.pop(context), // Logout simples (volta pra login)
            tooltip: "Sair",
          )
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : _userData == null
              ? const Center(child: Text("Erro ao carregar dados."))
              : Padding(
                  padding: const EdgeInsets.all(20.0),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        "Bem-vindo ao Sistema TCC",
                        style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold),
                      ),
                      const SizedBox(height: 20),
                      Card(
                        elevation: 4,
                        child: ListTile(
                          leading: const Icon(Icons.person, size: 40, color: Colors.green),
                          title: Text(_userData!['username']),
                          subtitle: Text(_userData!['email']),
                        ),
                      ),
                      const SizedBox(height: 20),
                      const Text("Status de Segurança:", style: TextStyle(fontWeight: FontWeight.bold)),
                      const SizedBox(height: 10),
                      const Row(
                        children: [
                          Icon(Icons.check_circle, color: Colors.green),
                          SizedBox(width: 10),
                          Text("Conexão Criptografada (Cloudflare)"),
                        ],
                      ),
                      const SizedBox(height: 10),
                      const Row(
                        children: [
                          Icon(Icons.shield, color: Colors.green),
                          SizedBox(width: 10),
                          Text("Autenticação via Token Ativa"),
                        ],
                      ),
                      const SizedBox(height: 20),
                      const Text("Ferramentas de Defesa:", style: TextStyle(fontWeight: FontWeight.bold)),
                      const SizedBox(height: 10),
                      Card(
                            elevation: 2,
                            child: ListTile(
                              leading: const Icon(Icons.travel_explore, color: Colors.blue),
                              title: const Text("Validar Conexão SSL"),
                              subtitle: const Text("Detectar ataques MitM em sites"),
                              trailing: const Icon(Icons.arrow_forward_ios),
                              onTap: () {
                                Navigator.push(
                                  context,
                                  MaterialPageRoute(
                                    // Passa a URL do servidor para a nova tela
                                    builder: (context) => SSLValidatorPage(baseUrl: widget.baseUrl,token: widget.token),
                                  ),
                                );
                              },
                            ),
                          ),
                      // Aqui você pode adicionar os botões de "Pânico" futuramente
                    ],
                  ),
                ),
    );
  }
}