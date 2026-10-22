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

## Como rodar

Com o [Docker Desktop](https://www.docker.com/products/docker-desktop/) aberto, na raiz do projeto:

```bash
cp .env.example .env
docker compose up -d --build --wait
```

Acesse **http://localhost:8080**. Detalhes em [docs/docker.md](docs/docker.md).

## Documentação

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

## Estrutura do repositório

```
├── backend_vet/            # API Flask (Python)
├── frontend_vet/           # páginas HTML/CSS/JS e configuração do Nginx
├── db/                     # schema.sql do PostgreSQL
├── docs/                   # documentação
├── docker-compose.yml      # sobe banco, backend e frontend
└── .env.example            # modelo das variáveis de ambiente
```

---

Projeto desenvolvido para fins acadêmicos nos Projetos Integradores III e IV do CEUB. © 2026 VetTrace.
