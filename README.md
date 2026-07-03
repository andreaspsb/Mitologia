# Mitologia

Base de conhecimento estruturada sobre mitologia grega, criada a partir do arquivo `Mitologia grega.drawio`.

O objetivo é transformar o diagrama em uma fonte de dados versionável, consultável e exportável. O draw.io passa a ser entrada inicial e futura saída gerada, não a fonte principal de manutenção.

## Stack inicial

- Backend: FastAPI, SQLAlchemy e Alembic.
- Banco: PostgreSQL.
- Frontend: Next.js, React e Cytoscape.js.
- Deploy alvo: Railway.
- Scripts: Python para parse, normalização, seed e exportações.

## Estrutura

```text
backend/      API FastAPI e modelos SQLAlchemy
frontend/     Site Next.js
scripts/      Parser, normalização, seed e exportadores
data/         Dados gerados localmente
alembic/      Migrações do banco
tests/        Testes dos scripts de dados
```

## Rodar o pipeline de dados

Use o Python disponível no ambiente. Neste Windows, se `python` não estiver no PATH, use o Python empacotado do Codex.

```powershell
python scripts/parse_drawio.py "Mitologia grega.drawio"
python scripts/normalize_entities.py
python scripts/normalize_relationships.py
```

Saídas geradas:

- `data/parsed/drawio_raw.json`
- `data/seed/entities.csv`
- `data/seed/aliases.csv`
- `data/seed/relationships.csv`

## Banco local

```powershell
docker compose up -d postgres
copy .env.example .env
alembic upgrade head
python scripts/seed_database.py
```

O Postgres local usa a porta `5433` para evitar conflito com instalações locais na porta `5432`.

## Backend

```powershell
uvicorn backend.app.main:app --reload
```

Endpoints iniciais:

- `GET /health`
- `GET /entities`
- `GET /entities/{id}`
- `GET /entities/{id}/relationships`
- `GET /relationships`
- `GET /search?q=zeus`
- `GET /audit/summary`

Os endpoints de relacionamentos retornam IDs e nomes das entidades de origem/destino, permitindo que o frontend renderize vínculos legíveis sem buscar a lista inteira de entidades.

## Auditoria dos dados

O site inclui a página `/audit`, que consome `GET /audit/summary` e mostra:

- totais de entidades e relacionamentos;
- entidades por tipo;
- relacionamentos por tipo;
- entidades ainda classificadas como `unknown`;
- relacionamentos `associated_with` que precisam de revisão.

## Busca

O site inclui a página `/search` e um formulário na home. A busca usa `GET /search?q=...` e retorna entidades encontradas por nome principal ou alias, com link para a página individual.

## Grafo

A página `/graph` carrega até 1000 entidades e 1000 relacionamentos e oferece filtros por tipo de entidade e tipo de relação. Relações cujas pontas ficam fora do filtro atual são ocultadas para manter o grafo consistente.

## Frontend

```powershell
cd frontend
npm install
npm run dev
```

Configure `NEXT_PUBLIC_API_BASE_URL` se a API não estiver em `http://localhost:8000`.

## Testes

```powershell
python -m pytest
cd frontend
npm run build
```

## Railway

Runbook detalhado com login, WSL, comandos validados, erros encontrados e recuperação: [docs/railway-runbook.md](docs/railway-runbook.md).

Ambiente publicado com auto-deploy via GitHub:

- Projeto: `Mitologia`.
- Repositório: `andreaspsb/Mitologia`.
- Branch de deploy: `main`.
- Backend: `https://mitologia-backend-production.up.railway.app`.
- Frontend: `https://mitologia-frontend-production.up.railway.app`.
- Postgres gerenciado no mesmo projeto.

As mudanças enviadas para `origin/main` disparam deploys automáticos no Railway.
Validação real: o commit `f50e674` (`Add audit entry points to home`) gerou deploy automático `SUCCESS` no frontend (`a8918bec-4529-4771-86b6-f35cca85464b`) e no backend (`f587760b-248d-4842-8b0b-07a4d24bbdc7`).

No Windows, use o Railway CLI pelo WSL para operações administrativas. Para deploys manuais de fallback, nunca publique direto de `/mnt/c`; copie o repositório para o filesystem nativo do WSL antes de executar `railway up`:

```bash
mkdir -p /tmp/mitologia-railway
cd "/mnt/c/Users/andre/Repositórios Git/Mitologia"
tar --exclude='.git' --exclude='frontend/node_modules' --exclude='frontend/.next' --exclude='node_modules' --exclude='.pytest_cache' --exclude='__pycache__' --exclude='*.egg-info' -cf - . | tar -C /tmp/mitologia-railway -xf -
cd /tmp/mitologia-railway
source ~/.railway/env
railway link --project de345e87-0bfc-4e1b-8629-d581eb03f04d
```

O projeto Railway tem três recursos:

- Postgres gerenciado.
- Serviço backend `mitologia-backend`.
- Serviço frontend `mitologia-frontend`.

Configuração dos serviços:

- Backend:
  - Source: `andreaspsb/Mitologia`, branch `main`, raiz do repositório.
  - Builder: Railpack.
  - Config versionada: `backend/railway.json`.
  - Watch paths desejados: `/backend/**`, `/alembic/**`, `/scripts/**`, `/pyproject.toml`, `/alembic.ini`.
  - Variáveis:
    - `DATABASE_URL=${{Postgres.DATABASE_URL}}`
    - `BACKEND_CORS_ORIGINS=https://mitologia-frontend-production.up.railway.app`
    - `RAILPACK_INSTALL_CMD=pip install --target ./.railway-packages .`
    - `RAILPACK_START_CMD=PYTHONPATH=/app/.railway-packages python -c "from alembic.config import main; main()" upgrade head && PYTHONPATH=/app/.railway-packages python scripts/bootstrap_database.py && PYTHONPATH=/app/.railway-packages python -m uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT`
  - O script `scripts/railway_set_backend_start.sh` reaplica os comandos Railpack do backend.
- Frontend:
  - Source: `andreaspsb/Mitologia`, branch `main`, root directory `/frontend`.
  - Builder: Dockerfile.
  - Dockerfile path no Railway: `/frontend/Dockerfile`.
  - Config versionada: `frontend/railway.json`.
  - Watch path desejado: `/frontend/**`.
  - Variável: `NEXT_PUBLIC_API_BASE_URL=https://mitologia-backend-production.up.railway.app`.

Deploy manual de fallback:

```bash
railway up --service mitologia-backend --environment production --ci --message "Deploy Mitologia backend"
railway up frontend --path-as-root --service mitologia-frontend --environment production --ci --message "Deploy Mitologia frontend"
```

O frontend roda no navegador do usuário, então `NEXT_PUBLIC_API_BASE_URL` deve apontar para o domínio público do backend. O backend usa o `DATABASE_URL` privado do Postgres gerenciado. URLs `postgresql://...` fornecidas pelo Railway são aceitas diretamente pela aplicação.

No backend, o start command executa `alembic upgrade head` e `python scripts/bootstrap_database.py` antes de iniciar o Uvicorn. O seed é idempotente: ele reprocessa `Mitologia grega.drawio` e atualiza entidades, aliases e relacionamentos no Postgres.
