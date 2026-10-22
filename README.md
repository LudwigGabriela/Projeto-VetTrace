# 🐾 VetTrace

<p align="center">
<img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white"/>
<img src="https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white"/>
<img src="https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white"/>
<img src="https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white"/>
<img src="https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white"/>
<img src="https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black"/>
<img src="https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white"/>
</p>

Sistema web de rastreabilidade de resíduos de saúde, cadáveres e materiais esterilizados da
clínica veterinária do CEUB, seguindo a RDC 222/2018 da ANVISA.
Projeto Integrador III e IV — Ciência da Computação.


## 📌 Sobre o Projeto

O **VetTrace** é um sistema de rastreabilidade e gerenciamento desenvolvido para clínicas veterinárias, com o objetivo de centralizar o controle de materiais esterilizados, gerenciamento de resíduos e registros operacionais.

A plataforma permite acompanhar todo o ciclo de vida dos materiais utilizados no ambiente clínico, garantindo maior controle, segurança e organização dos processos.

O projeto foi desenvolvido seguindo conceitos de:

- Engenharia de Software
- Banco de Dados Relacional
- Desenvolvimento Web
- Controle de acesso por usuários
- Auditoria e rastreabilidade de informações


---

# 🚀 Funcionalidades


## 🔐 Autenticação e Usuários

- Cadastro de usuários
- Login seguro com autenticação
- Controle de permissões por perfil:
  - Administrador
  - Técnico
  - Solicitante
- Gerenciamento de perfil do usuário


## 🧪 Gestão de Materiais Esterilizados

- Cadastro de materiais
- Controle de estoque
- Acompanhamento do ciclo de esterilização
- Controle de status:

```
Sujo
↓
Em esterilização
↓
Esterilizado
↓
Em uso
```


## 🗑️ Gestão de Resíduos

- Registro de resíduos gerados
- Classificação por tipo:

  - Infectante
  - Comum
  - Perfurocortante

- Controle de quantidade
- Registro de origem
- Histórico para auditoria


## 🐾 Rastreabilidade de Cadáveres

- Registro de entrada: espécie, identificação, proprietário, causa do óbito e destino previsto
- Registro de saída e das empresas de coleta


## 📊 Dashboard

Painel administrativo contendo:

- Quantidade de materiais cadastrados
- Resíduos registrados
- Status dos ciclos
- Indicadores gerais do sistema


## 📄 Relatórios

- Consulta de registros
- Filtros por período
- Histórico das operações realizadas


---

# 👤 Perfis de Usuário


| Perfil | Permissões |
|---|---|
| Admin | Controle completo do sistema |
| Técnico | Operações clínicas e materiais |
| Solicitante | Solicitação de materiais |


---

# 🏗️ Arquitetura do Sistema


```
VetTrace

├── Frontend
│   ├── HTML5
│   ├── CSS3
│   └── JavaScript
│
├── Backend
│   ├── Python
│   ├── Flask API
│   └── JWT Authentication
│
└── Banco de Dados
    └── PostgreSQL
```


Cada parte roda em um container Docker, e eles conversam em cadeia:

```
navegador ──► frontend (Nginx) ──► backend (Flask + Gunicorn) ──► banco (PostgreSQL 18)
```


---

# 🛠️ Tecnologias Utilizadas


## Backend

- Python
- Flask
- Flask-JWT-Extended
- Psycopg2
- Werkzeug


## Frontend

- HTML5
- CSS3
- JavaScript
- Bootstrap


## Banco de Dados

- PostgreSQL


## Infraestrutura

- Docker e Docker Compose
- Nginx
- Gunicorn


---

# ▶️ Como Rodar


Com o [Docker Desktop](https://www.docker.com/products/docker-desktop/) aberto, na raiz do projeto:


```bash
cp .env.example .env
docker compose up -d --build --wait
```


Acesse **http://localhost:8080**. O banco já vem criado, com todas as tabelas.

- Se você já tem PostgreSQL instalado no computador, use `POSTGRES_PORT=5433` no `.env`.
- No primeiro acesso, crie um usuário na tela de cadastro (CRMV no formato `DF-12345`) e faça login com ele.
- Para rodar o backend fora do Docker, veja [docs/backend.md](docs/backend.md#7-rodar-sem-docker).

Comandos do dia a dia e solução de problemas: [docs/docker.md](docs/docker.md).


---

# 📚 Documentação

Toda a documentação fica em [`docs/`](docs/).

| Documento | Conteúdo |
|---|---|
| [Sobre o projeto](docs/sobre-o-projeto.md) | objetivo, funcionalidades, perfis de usuário, interface e equipe |
| [Docker](docs/docker.md) | como rodar, arquitetura dos containers, comandos e problemas comuns |
| [Backend](docs/backend.md) | estrutura da API, rotas, autenticação, execução sem Docker e decisões de arquitetura |
| [Frontend](docs/frontend.md) | estrutura e mapa das páginas, convenções, design e decisões de arquitetura |
| [Banco de dados](docs/banco-de-dados.md) | schema, tabelas, conexão, backup e decisões de arquitetura |
| [Contribuindo](docs/contribuindo.md) | Git, branches, commits e dependências |
| [Acadêmico](docs/academico/) | Documento de Visão, histórias de usuário, critérios de aceitação, regras de negócio e relatórios |


---

# 📂 Estrutura de Pastas


```
VetTrace

├── backend_vet/            # API Flask (Python)
├── frontend_vet/           # páginas HTML/CSS/JS e configuração do Nginx
├── db/                     # schema.sql do PostgreSQL
├── docs/                   # documentação
├── docker-compose.yml      # sobe banco, backend e frontend
├── .env.example            # modelo das variáveis de ambiente
└── README.md
```


---

# 🎨 Interface


![Dashboard VetTrace](https://github.com/user-attachments/assets/632388b4-6449-4d80-b2e9-fbf5b686d602)



Protótipo:

[Figma - VetTrace](https://www.figma.com/make/8uLDzoqZsqzk8zLYMic0pg/Veterinary-Management-Dashboard-Wireframe)

Wireflow, Canva e wireframe: [docs/frontend.md](docs/frontend.md#8-design-e-protótipos).


---

# 📈 Próximas Melhorias

- [ ] Controle completo de permissões
- [ ] Exportação de relatórios PDF
- [ ] Histórico completo de auditoria
- [ ] Dashboard com gráficos avançados
- [ ] Notificações internas


---

# 👥 Equipe de Desenvolvimento


| Nome | Função | GitHub |
|---|---|---|
| **Caio Peliz** | Scrum Master & Desenvolvedor | [@caiocardoso418](https://github.com/caiocardoso418) |
| **Gabriela Ludwig** | Product Owner & Desenvolvedora | [@LudwigGabriela](https://github.com/LudwigGabriela) |
| **Juan Talyson** | Database Administrator | [@juantalyson](https://github.com/juantalyson) |
| **Maria Elis** | UI/UX Designer & Documentação | [@mariaelis23](https://github.com/mariaelis23) |
| **Carlos Eduardo** | Tech Leader & Arquitetura | [@karlosmafra](https://github.com/karlosmafra) |


---

# 📄 Licença

Projeto desenvolvido para fins acadêmicos nos Projetos Integradores III e IV.

© 2026 VetTrace
