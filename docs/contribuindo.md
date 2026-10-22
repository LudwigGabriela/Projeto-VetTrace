# Contribuindo

Como o time trabalha no repositório: primeiros passos, branches, commits e dependências.

## Primeiros passos

```bash
git clone https://github.com/LudwigGabriela/ProjetoIntegrador3.git
cd ProjetoIntegrador3
cp .env.example .env
docker compose up -d --build --wait
```

Detalhes em [docker.md](docker.md). Para rodar o backend fora do Docker, veja
[backend.md](backend.md#7-rodar-sem-docker).

---

## Fluxo de branches

```text
main
  └── feature/nome-da-feature
```

Exemplos: `feature/cadastro-residuos`, `feature/dashboard`, `feature/login`.

---

## Comandos Git do dia a dia

```bash
git pull                                # atualizar o projeto
git branch                              # ver a branch atual
git checkout -b feature/nova-feature    # criar uma branch
git add .                               # preparar as alterações
git commit -m "feat: descrição"         # registrar
git push                                # enviar
```

---

## Boas práticas

- Sempre crie uma branch para novas funcionalidades.
- Atualize a `main` antes de começar uma tarefa.
- Faça commits pequenos e organizados, com mensagem em português.
- Nunca suba `venv/` nem arquivos `.env` (já estão no `.gitignore`).
- Variável de ambiente nova: adicione ao `.env.example` e à tabela de
  [docker.md](docker.md#6-variáveis-de-ambiente).
- Mudou o `db/schema.sql`? Avise o grupo: todos precisam recriar o banco — ver
  [banco-de-dados.md](banco-de-dados.md#alterar-o-schema).
- Documentação nova vai em `docs/`.

---

## Dependências do backend

Adicione a biblioteca ao `backend_vet/requirements.txt` à mão, com a versão fixada (por exemplo,
`requests==2.32.3`), e reconstrua a imagem com `docker compose up -d --build`.

> ⚠️ Evite `pip freeze > requirements.txt`. O `pywin32` e o `pypiwin32` têm o marcador
> `; sys_platform == "win32"` (só existem para Windows) e o `pip freeze` apaga esse marcador —
> sem ele, o build da imagem Docker (Linux) quebra. Se usar o `pip freeze`, recoloque os
> marcadores depois.
