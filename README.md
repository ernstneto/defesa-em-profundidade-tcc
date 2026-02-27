# 🛡️ Defesa em Profundidade: Proteção contra Phishing e MitM

Este repositório contém a implementação prática e a Prova de Conceito (PoC) do meu Trabalho de Conclusão de Curso (TCC). O foco do projeto é demonstrar uma arquitetura de segurança multicamadas (Defense in Depth) para mitigar ataques de Phishing e Man-in-the-Middle (MitM).

📄 **[Leia a Monografia Completa Aqui](./documentacao/nome_do_seu_arquivo.pdf)** *(Lembre-se de ajustar este link para o nome real do seu PDF)*

## 🏗️ Arquitetura do Projeto

O ecossistema de segurança foi desenhado atuando em diferentes frentes de proteção:

* **Camada de Rede (Firewall):** Utilização do **pfSense** como barreira principal e filtro de tráfego malicioso.
* **Camada de Aplicação (Desktop):** Ferramenta de scanner de segurança empacotada com Python (PyInstaller), responsável por auditorias e criação de túneis seguros.
* **Camada Mobile (PoC):** Aplicativo desenvolvido em **Flutter/Dart** demonstrando defesas ativas do lado do cliente, implementando:
  * **SSL Pinning:** Prevenção contra interceptação de tráfego e certificados falsos.
  * **Kill Switch:** Mecanismo de interrupção de emergência em caso de violação de integridade.

## 📂 Estrutura do Repositório

- `/tcc_security_project`: Scripts Python e automação de túneis de segurança.
- `/TCC_SECURITY_APP`: Código-fonte da Prova de Conceito Mobile (Flutter).
- `/documentacao`: Documentação acadêmica e detalhamento técnico das regras do pfSense.

## 🚀 Tecnologias Utilizadas

- **Segurança de Rede:** pfSense
- **Mobile:** Flutter, Dart
- **Automação/Desktop:** Python, Shell Script

---
*Desenvolvido como requisito para conclusão de curso e demonstração de práticas aplicadas de Information Security.*