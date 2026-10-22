# Frontend

Interface web do VetTrace: páginas HTML, CSS e JavaScript puros, sem framework e sem etapa
de build. Este guia explica a estrutura, o que cada página faz, as convenções, como o
frontend conversa com a API e as decisões de arquitetura.

## Sumário

1. [Visão geral](#1-visão-geral)
2. [Estrutura de pastas](#2-estrutura-de-pastas)
3. [Mapa das páginas](#3-mapa-das-páginas)
4. [Como uma página funciona](#4-como-uma-página-funciona)
5. [Convenções](#5-convenções)
6. [Comunicação com a API](#6-comunicação-com-a-api)
7. [Como rodar](#7-como-rodar)
8. [Design e protótipos](#8-design-e-protótipos)
9. [Decisões de arquitetura](#9-decisões-de-arquitetura)

---

## 1. Visão geral

| Item | Escolha |
|---|---|
| Páginas | HTML estático, em `paginas/` |
| Estilo | `estilos/styles.css`, mais Bootstrap 5.3.8 nas telas de descarte e edição |
| Scripts | JavaScript puro, um arquivo por página |
| Bibliotecas | por CDN: Bootstrap 5.3.8, Chart.js 4.4.0 e a fonte Inter (Google Fonts) |
| Servidor | Nginx no Docker (`http://localhost:8080`); Live Server fora do Docker |

---

## 2. Estrutura de pastas

```
frontend_vet/
├── paginas/               # as 14 telas (.html)
├── js/                    # um script por página
│   └── utils/
│       ├── usuario.js     # confere a sessão e preenche o menu lateral
│       └── notificacao.js # mostrarMensagem(): exibe avisos (hoje, um alert)
├── estilos/
│   └── styles.css         # estilo das telas internas
├── assets/                # logo
├── nginx.conf             # configuração do Nginx no Docker
├── Dockerfile
└── .dockerignore
```

---

## 3. Mapa das páginas

| Página | Scripts | Chamadas à API | Situação |
|---|---|---|---|
| `login.html` | `login.js` | `POST /api/auth/login` | funcional |
| `cadastro.html` | `cadastro.js` | `POST /api/auth/cadastro` | funcional |
| `descarte-residuos.html` | `utils/notificacao.js`, `utils/usuario.js`, `descarte-residuos.js` | `GET` e `POST /residuo`, `GET /residuo/peso-total` | funcional |
| `editar-residuo.html` | `editar-residuo` | `GET /residuo`, `PUT /residuo/<id>` | funcional |
| `descarte-cadaver.html` | `utils/notificacao.js`, `utils/usuario.js`, `descarte-cadaver.js` | `GET` e `POST /cadaver` | funcional |
| `editar-cadaver.html` | `editar-cadaver.js` | `GET /cadaver`, `PUT /cadaver/<id>` | funcional |
| `relatorios.html` | `utils/notificacao.js`, `utils/usuario.js`, `relatorio-residuos.js` | `GET /residuo`, `GET /residuo/peso-total` | parcial: tabela e totais reais |
| `perfil.html` | `perfil.js` | — | mostra os dados do usuário logado, sem edição |
| `dashboard.html` | `utils/usuario.js` | — | protótipo, com dados fixos |
| `estoque-esteril.html` | `utils/usuario.js` | — | protótipo |
| `ciclos.html` | `utils/usuario.js` | — | protótipo |
| `registrar-material.html` | `utils/usuario.js` | — | protótipo |
| `relatorio-esterilizacao.html` | `utils/usuario.js` | — | protótipo |
| `solicitar-material.html` | script na própria página, `utils/usuario.js` | — | protótipo: valida e exibe um alerta, sem salvar |

O Chart.js é carregado em `dashboard`, `ciclos`, `relatorios` e `relatorio-esterilizacao`,
mas nenhum gráfico é desenhado ainda. O `js/solicitar-material.js` não é carregado por nenhuma
página.

---

## 4. Como uma página funciona

1. O `<head>` carrega a fonte, o `styles.css` e, quando usadas, as bibliotecas por CDN.
2. Os scripts ficam no fim do `<body>`: primeiro os utilitários, depois o script da página.
3. O `utils/usuario.js` lê o `usuario` do `localStorage`. Se não houver, redireciona para o
   `login.html`; se houver, preenche nome, perfil e iniciais no menu lateral.
4. O script da página registra os eventos (cliques, envio de formulário) e chama a API com
   `fetch`.

---

## 5. Convenções

- **Um script por página**, em `js/<nome-da-pagina>.js`, carregado no fim do `<body>`. O que é
  usado por mais de uma página vai em `js/utils/`.
- **IDs de formulário:** `form-<entidade>-input-<campo>` e `form-<entidade>-btn-<ação>` — por
  exemplo, `form-residuo-input-peso` e `form-residuo-btn-submit`.
- **Utilitários:** páginas internas carregam o `utils/usuario.js`; quem usa `mostrarMensagem()`
  carrega também o `utils/notificacao.js`.
- **Português** nos nomes de funções e variáveis (`carregarResiduos`, `preencherTabela`).
- **Dados da API na tela:** prefira `textContent` a `innerHTML` (ver ADR-008).

---

## 6. Comunicação com a API

- O endereço `http://127.0.0.1:5000` está escrito direto em cada script que chama a API (7
  arquivos). No Docker, quem responde nessa porta é o Nginx, que repassa para o backend — ver
  [docker.md](docker.md#3-como-os-containers-se-comunicam).
- As requisições enviam `Content-Type: application/json` e, nas rotas de escrita,
  `Authorization: Bearer <token>`.
- As mensagens de erro chegam em `data.erro` ou `data.msg`.
- As telas de edição buscam a lista inteira (`GET /residuo`, `GET /cadaver`) e filtram pelo
  `id` da URL (`?id=`), porque a API ainda não tem consulta por id.

Rotas e corpos das requisições: [backend.md](backend.md#4-rotas-da-api).

---

## 7. Como rodar

**Com Docker (recomendado):** http://localhost:8080 — ver [docker.md](docker.md). Depois de
editar arquivos, rode `docker compose up -d --build frontend`, ou deixe o
`docker compose watch` aberto para as mudanças aparecerem na hora.

**Sem Docker:** abra `paginas/login.html` com o Live Server do VS Code, ou rode
`python -m http.server 5500` dentro de `frontend_vet/` e acesse
http://127.0.0.1:5500/paginas/login.html. A API precisa estar respondendo em `127.0.0.1:5000`.

---

## 8. Design e protótipos

| Material | Link |
|---|---|
| Protótipo do site (Figma) | [abrir](https://www.figma.com/make/8uLDzoqZsqzk8zLYMic0pg/Veterinary-Management-Dashboard-Wireframe?t=HzyuMSq0NA6IXz63-1&preview-route=%2Frelatorios) |
| Wireflow: fluxo entre as telas (Figma) | [abrir](https://www.figma.com/make/iBktCaRpQg49p6HaZVTSMr/Wireflow-Diagram-for-VetTrace?fullscreen=1&t=Xpv6lxc3WSBpx4XX-1) |
| Projeto no Figma Make | [abrir](https://www.figma.com/make/8uLDzoqZsqzk8zLYMic0pg?type=figmake) |
| Canva | [abrir](https://canva.link/rdcto4n5dxvdap5) |

**Wireframe**

![Wireframe do VetTrace](imagens/wireframe-vettrace.jpg)

---

## 9. Decisões de arquitetura

Registros de decisão (ADRs) do frontend. São registros retroativos: documentam decisões já
implementadas e as consequências que elas trazem hoje. Backend em
[backend.md](backend.md#9-decisões-de-arquitetura); infraestrutura em
[docker.md](docker.md#9-decisões-de-arquitetura); banco em
[banco-de-dados.md](banco-de-dados.md#decisões-de-arquitetura).

### ADR-005 · HTML, CSS e JavaScript puros, sem framework nem build

- **Status:** aceita
- **Contexto:** equipe com níveis diferentes de experiência, entregas por sprint e telas
  formadas basicamente por formulários e tabelas.
- **Decisão:** páginas HTML estáticas, JavaScript sem framework e um CSS próprio
  (`styles.css`). Sem npm, bundler ou etapa de build.
- **Consequências:** ✅ qualquer pessoa edita e vê o resultado com F5; ✅ servir é simples
  (Live Server ou Nginx). ⚠️ sem componentes reutilizáveis: o menu lateral se repete em 10
  páginas, e mudar o layout exige editar todas; ⚠️ `login.html` e `cadastro.html` têm o CSS
  na própria página, separado do `styles.css`.

### ADR-006 · Um script por página, utilitários compartilhados e IDs padronizados

- **Status:** aceita
- **Contexto:** várias pessoas trabalhando em telas diferentes ao mesmo tempo.
- **Decisão:** cada página tem o seu `js/<pagina>.js`; o que é compartilhado fica em
  `js/utils/` (`usuario.js` para sessão e menu, `notificacao.js` para mensagens). Os IDs seguem
  `form-<entidade>-input-<campo>` e `form-<entidade>-btn-<ação>`.
- **Consequências:** ✅ é fácil achar o código de uma tela, e duas pessoas raramente mexem no
  mesmo arquivo; ✅ IDs previsíveis. ⚠️ as funções são globais: dois scripts carregados na
  mesma página não podem ter funções com o mesmo nome; ⚠️ é fácil esquecer um utilitário — as
  páginas `editar-residuo.html` e `editar-cadaver.html` usam `mostrarMensagem()` sem carregar o
  `notificacao.js`; ⚠️ o `js/editar-residuo` está sem a extensão `.js` (o Nginx tem uma regra
  só para ele).

### ADR-007 · Bibliotecas carregadas por CDN, com versão fixada

- **Status:** aceita
- **Contexto:** sem etapa de build, não existe `npm install`.
- **Decisão:** Bootstrap 5.3.8, Chart.js 4.4.0 e a fonte Inter vêm de CDN (jsDelivr e Google
  Fonts), com a versão escrita na URL.
- **Consequências:** ✅ nada para instalar; ✅ a versão fixa evita mudanças inesperadas. ⚠️ sem
  internet, as páginas perdem estilos e fonte; ⚠️ o Bootstrap convive com o `styles.css` nas
  telas de descarte e edição — atenção a classes com o mesmo nome.

### ADR-008 · Sessão no localStorage e token no cabeçalho Authorization

- **Status:** aceita
- **Contexto:** a API usa JWT e não mantém sessão (ver ADR-003, em [backend.md](backend.md#adr-003--autenticação-sem-estado-com-jwt)).
- **Decisão:** depois do login, o `login.js` guarda o `token` e o `usuario` no `localStorage`.
  As páginas internas usam o `utils/usuario.js` para exigir login, e as chamadas de escrita
  enviam `Authorization: Bearer <token>`.
- **Consequências:** ✅ simples, sem cookies. ⚠️ a proteção das páginas é só visual — quem
  garante o acesso é a API; ⚠️ qualquer script injetado na página consegue ler o token, por
  isso dados vindos da API devem ir para a tela com `textContent` (hoje as tabelas ainda usam
  `innerHTML`); ⚠️ nenhum script limpa o `localStorage`: não há logout de verdade; ⚠️ o
  `localStorage` é separado por endereço — Live Server e Docker têm sessões diferentes.
