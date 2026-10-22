# Sobre o projeto

O **VetTrace** é um sistema web de rastreabilidade e gerenciamento para a clínica veterinária
do CEUB. Ele centraliza o controle de resíduos de saúde, de cadáveres e de materiais
esterilizados, registrando data, hora e responsável em cada operação, como exige a
**RDC 222/2018 da ANVISA**.

O projeto foi desenvolvido nos Projetos Integradores III e IV do curso de Ciência da
Computação e aplica conceitos de:

- Engenharia de Software
- Banco de Dados Relacional
- Desenvolvimento Web
- Controle de acesso por usuários
- Auditoria e rastreabilidade de informações

---

## 🚀 Funcionalidades

### 🗑️ Gestão de resíduos

- Registro dos resíduos gerados, por grupo: A (infectantes), B (químicos), D (comuns) e
  E (perfurocortantes)
- Controle de quantidade e registro do setor de origem, com data e hora
- Destino do resíduo, com histórico para auditoria
- Consulta com filtros por período

### 🐾 Cadáveres

- Registro de entrada: espécie, identificação, proprietário, causa do óbito e destino previsto
- Registro de saída e das empresas de coleta

### 🧪 Materiais esterilizados

- Cadastro de materiais e controle de estoque
- Acompanhamento do ciclo de esterilização
- Controle de status:

```
Sujo → Em esterilização → Esterilizado → Em uso
```

### 📊 Dashboard

Painel administrativo com a quantidade de materiais cadastrados, os resíduos registrados, o
status dos ciclos e os indicadores gerais do sistema.

### 📄 Relatórios

- Consulta de registros
- Filtros por período
- Histórico das operações realizadas

### 🔐 Autenticação e usuários

- Cadastro de usuários e login
- Controle de permissões por perfil
- Gerenciamento do perfil do usuário

> O que já funciona em cada tela está no [mapa das páginas](frontend.md#3-mapa-das-páginas).

---

## 👤 Perfis de usuário

| Perfil | Permissões |
|---|---|
| Administrador | controle completo do sistema |
| Técnico | operações clínicas e materiais |
| Solicitante | solicitação de materiais, consultas e registros |

---

## 🏗️ Arquitetura

```
navegador ──► frontend (Nginx) ──► backend (Flask + Gunicorn) ──► banco (PostgreSQL 18)
```

Cada parte roda num container Docker. Detalhes em [docker.md](docker.md),
[backend.md](backend.md), [frontend.md](frontend.md) e [banco-de-dados.md](banco-de-dados.md).

---

## 🛠️ Tecnologias

| Camada | Tecnologias |
|---|---|
| Backend | Python 3.14, Flask, Flask-JWT-Extended, psycopg2, Werkzeug, Gunicorn |
| Frontend | HTML5, CSS3, JavaScript, Bootstrap 5, Chart.js |
| Banco de dados | PostgreSQL 18 |
| Infraestrutura | Docker, Docker Compose, Nginx |

---

## 🎨 Interface

![Dashboard VetTrace](https://github.com/user-attachments/assets/632388b4-6449-4d80-b2e9-fbf5b686d602)

Protótipo, wireflow e wireframe: [frontend.md — Design e protótipos](frontend.md#8-design-e-protótipos).

---

## 📈 Próximas melhorias

- [ ] Controle completo de permissões
- [ ] Exportação de relatórios PDF
- [ ] Histórico completo de auditoria
- [ ] Dashboard com gráficos avançados
- [ ] Notificações internas

---

## 👥 Equipe de desenvolvimento

| Nome | Função | GitHub |
|---|---|---|
| **Caio Peliz** | Scrum Master & Desenvolvedor | [@caiocardoso418](https://github.com/caiocardoso418) |
| **Gabriela Ludwig** | Product Owner & Desenvolvedora | [@LudwigGabriela](https://github.com/LudwigGabriela) |
| **Juan Talyson** | Database Administrator | [@juantalyson](https://github.com/juantalyson) |
| **Maria Elis** | UI/UX Designer & Documentação | [@mariaelis23](https://github.com/mariaelis23) |
| **Carlos Eduardo** | Tech Leader & Arquitetura | [@karlosmafra](https://github.com/karlosmafra) |

---

## 📚 Documentos acadêmicos

Documento de Visão, histórias de usuário, critérios de aceitação, regras de negócio, o modelo
do Projeto Integrador, o relatório de desenvolvimento e a página do projeto no Notion estão em
[academico/](academico/).

---

## 📄 Licença

Projeto desenvolvido para fins acadêmicos nos Projetos Integradores III e IV. © 2026 VetTrace.
