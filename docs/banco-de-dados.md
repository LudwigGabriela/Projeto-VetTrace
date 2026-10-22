# Banco de dados

O banco roda em um container Docker. Cada pessoa do time roda o **seu próprio** container
localmente — o que compartilhamos é a *estrutura* do banco (`db/schema.sql`), não os dados.

Este guia cobre só o banco. A stack completa (banco + backend + frontend) está em
[docker.md](docker.md).

---

## Pré-requisito

Docker Desktop instalado e em execução.
No Windows, ative a integração com WSL: **Settings → Resources → WSL Integration**.

Verifique:

```bash
docker --version
docker ps
```

Se `docker ps` der *permission denied* no WSL:

```bash
sudo usermod -aG docker $USER
```

Depois feche o terminal e rode `wsl --shutdown` no PowerShell.

---

## Subir o banco

Na raiz do projeto:

```bash
cp .env.example .env    # só na primeira vez
docker compose up -d --wait db
```

O `db` no final sobe só o banco (sem ele, o `up` sobe também o backend e o frontend).
O `--wait` faz o comando esperar o banco ficar `healthy`, não só "iniciado".

Pronto. O container sobe e **aplica o schema automaticamente** na primeira inicialização:
as 13 tabelas, os índices, os triggers e os dados de referência (destinos, categorias,
autoclaves e kits) já vêm criados. Ninguém precisa rodar SQL na mão.

### Se você já tem PostgreSQL instalado na máquina

A porta 5432 estará ocupada e o container não sobe. Edite seu `.env`:

```
POSTGRES_PORT=5433
DATABASE_URL=postgresql://vettrace:vettrace@localhost:5433/vettrace
```

O `.env` é local e não vai para o Git — cada um ajusta o seu.

---

## Verificar se funcionou

```bash
docker compose ps                                            # db deve estar "healthy"
docker compose exec db psql -U vettrace -d vettrace -c "\dt" # deve listar 13 tabelas
```

Se o `psql` reclamar de socket logo após um `up -d` **sem** `--wait`, espere ~10 segundos:
o Postgres ainda está inicializando. O `docker compose up -d` retorna quando o container
*inicia*, não quando o banco fica *pronto*.

---

## Tabelas

| Tabela | Guarda |
|---|---|
| `usuarios` | usuários do sistema e o perfil de acesso (`admin`, `tecnico`, `solicitante`) |
| `residuos` | resíduos do PGRSS — grupo (A, B, D, E), quantidade, setores de origem e destino, responsável |
| `cadaveres` | cadáveres recebidos — espécie, proprietário, causa do óbito, entrada, saída, destino e status |
| `destinos_cadaver` | tabela de apoio: `labocien`, `empresa_terceirizada`, `proprietario` |
| `retiradas_cadaver` | saídas de cadáveres; o trigger `trg_retirada_cadaver` marca o cadáver como `retirado` |
| `empresas` | empresas de coleta e descarte |
| `categorias_descarte` | categorias de descarte de materiais (kit de sutura, caixas, perfurocortantes...) |
| `descartes` | registros de descarte de materiais |
| `autoclaves` | equipamentos de esterilização |
| `kits` | kits e caixas cirúrgicas que passam pela esterilização |
| `ciclos_esterilizacao` | cada ciclo de esterilização e seu status (`pendente`, `efetivo`, `inefetivo`) |
| `ciclo_kits` | quais kits entraram em cada ciclo |
| `validacoes_ciclo` | validação de um ciclo; o trigger `trg_validacao_ciclo` atualiza o status do ciclo |

Hoje a API usa `usuarios`, `residuos` e `cadaveres`. As demais já existem para os próximos
módulos (saída de cadáveres, empresas de coleta e materiais esterilizados).

---

## Comandos do dia a dia

| Ação | Comando |
|---|---|
| Subir só o banco | `docker compose up -d --wait db` |
| Parar (mantém dados) | `docker compose stop` |
| Parar e remover containers | `docker compose down` |
| **Zerar o banco** | `docker compose down -v && docker compose up -d --wait db` |
| Ver logs | `docker compose logs -f db` |
| Abrir o psql | `docker compose exec db psql -U vettrace -d vettrace` |

⚠️ O `-v` no `down` apaga o volume — **todos os dados são perdidos**. É a forma
correta de recomeçar do zero, mas não tem volta.

---

## Backup e restauração

**Backup**

```bash
mkdir backups
docker compose exec db pg_dump -U vettrace -d vettrace -Fc -f /tmp/vettrace.dump
docker cp vettrace-db:/tmp/vettrace.dump ./backups/vettrace_AAAA-MM-DD.dump
docker compose exec db rm /tmp/vettrace.dump
```

- `-Fc` gera o formato *custom*: compactado e restaurável tabela a tabela.
- O dump é gravado **dentro** do container e copiado com `docker cp` porque, no PowerShell,
  `docker compose exec ... pg_dump > arquivo` corrompe o arquivo binário.
- `backups/` e `*.dump` estão no `.gitignore`: o dump contém dados pessoais e hashes de senha.

**Restauração**

```bash
docker cp ./backups/vettrace_AAAA-MM-DD.dump vettrace-db:/tmp/restore.dump
docker compose stop backend               # ninguém escrevendo durante a restauração
docker compose exec db pg_restore -U vettrace -d vettrace --clean --if-exists /tmp/restore.dump
docker compose start backend
```

---

## Conectar por DBeaver / pgAdmin

| Campo | Valor |
|---|---|
| Host | `localhost` |
| Porta | `5432` (ou `5433`, conforme seu `.env`) |
| Banco | `vettrace` |
| Usuário | `vettrace` |
| Senha | `vettrace` |

A porta só aceita conexões **desta máquina** (`127.0.0.1`): ninguém na mesma rede Wi-Fi
consegue chegar ao banco, que usa a senha padrão publicada no GitHub.

---

## Alterar o schema

O `db/schema.sql` é a **fonte de verdade** da estrutura do banco. Toda mudança
(nova tabela, nova coluna, novo índice) passa por ele.

1. Edite `db/schema.sql`
2. Recrie o banco: `docker compose down -v && docker compose up -d --wait db`
3. Teste
4. Commit numa branch e abra PR

O schema **não** é aplicado em bancos já existentes — só na primeira inicialização
do volume. Por isso o passo 2 é obrigatório para ver a mudança.

Não existe migration automática. Se alguém alterar o schema, avise no grupo:
todos precisam rodar `down -v && up -d` para ficar com a mesma estrutura.

---

## Como funciona por baixo

- **Imagem**: `postgres:18` — versão fixada de propósito. `latest` muda com o tempo
  e um cluster criado por uma versão não abre em outra major version.
- **Volume**: `vettrace-data` montado em `/var/lib/postgresql`. A partir do Postgres 18,
  os dados ficam em `/var/lib/postgresql/18/docker` — por isso o volume monta um nível
  acima, e **não** em `/var/lib/postgresql/data` como mostram tutoriais antigos.
- **Schema automático**: `db/schema.sql` é montado em `/docker-entrypoint-initdb.d/`.
  A imagem oficial executa qualquer `.sql` desse diretório na primeira inicialização.
- **Porta**: publicada como `127.0.0.1:${POSTGRES_PORT}` — só para DBeaver/pgAdmin e para
  rodar o Flask fora do Docker. O backend em container usa a porta interna: `db:5432`.
- **Rede**: o banco fica só na rede `rede-dados`, junto com o backend. O frontend (Nginx)
  está em outra rede e não alcança o banco.
- **Healthcheck**: `pg_isready -h 127.0.0.1` testa via TCP. Durante a primeira inicialização
  o Postgres roda o `schema.sql` escutando só no socket local, então o banco só fica
  `healthy` — e o backend só sobe — depois que o schema terminou.

---

## Problemas comuns

**`port is already allocated`**
Algo já usa a porta. Mude `POSTGRES_PORT` no `.env` para 5433.

**Container sobe e morre**
`docker compose logs db` mostra o motivo. Erro de sintaxe no `schema.sql` derruba
a inicialização inteira.

**Alterei o `schema.sql` e nada mudou**
O schema só roda com o volume vazio. Rode `docker compose down -v && docker compose up -d`.

**`No such file or directory` no socket**
O banco ainda está inicializando. Espere alguns segundos e tente de novo.

**Outro computador não consegue conectar**
Proposital: a porta só escuta em `127.0.0.1`. Para liberar na rede, tire o `127.0.0.1:`
da linha `ports` do serviço `db` no `docker-compose.yml` — e troque a senha padrão antes.

---

## Decisões de arquitetura

Registro de decisão (ADR) do banco. As demais ADRs estão em
[backend.md](backend.md#9-decisões-de-arquitetura) (001 a 004),
[frontend.md](frontend.md#9-decisões-de-arquitetura) (005 a 008) e
[docker.md](docker.md#9-decisões-de-arquitetura) (010 a 013).

### ADR-009 · Schema versionado em `db/schema.sql`, aplicado automaticamente

- **Status:** aceita
- **Contexto:** as tabelas só existiam na máquina de quem as criou; quem clonava o projeto
  não conseguia rodá-lo.
- **Decisão:** o `db/schema.sql` é a fonte da verdade da estrutura — tabelas, CHECKs, índices,
  triggers e dados de referência — e é montado em `/docker-entrypoint-initdb.d/`, que o
  PostgreSQL executa na primeira inicialização de um volume vazio. Não há ferramenta de
  migration.
- **Consequências:** ✅ clonar e rodar `docker compose up` entrega o banco pronto; ✅ a
  estrutura é revisada por pull request, como o código. ⚠️ mudar o schema exige recriar o
  banco (`down -v`), o que apaga os dados locais; ⚠️ todo o time precisa recriar o banco a cada
  mudança — avise no grupo.