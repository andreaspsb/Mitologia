# Runbook Railway - Mitologia

Este documento registra o caminho validado para operar o deploy do projeto Mitologia no Railway, incluindo login, WSL, criacao de recursos, variaveis, deploy, verificacao e os erros que ja aconteceram.

O objetivo pratico: nao repetir a investigacao. Se precisar mexer no Railway de novo, siga este arquivo antes de tentar caminhos alternativos.

## Estado atual validado

- Projeto Railway: `Mitologia`
- Project ID: `de345e87-0bfc-4e1b-8629-d581eb03f04d`
- Environment: `production`
- Postgres service ID: `fd15f21f-a03e-4dbf-87fc-523c542275f5`
- Backend service: `mitologia-backend`
- Backend service ID: `9bea7d3f-b6ab-410b-ae70-8b1af55ea220`
- Backend URL: `https://mitologia-backend-production.up.railway.app`
- Frontend service: `mitologia-frontend`
- Frontend service ID: `ef2855b0-eb26-45ef-9733-d024ab8be034`
- Frontend URL: `https://mitologia-frontend-production.up.railway.app`
- Deploy frontend validado: `e23393b2-b460-4d7e-ad45-018f47975f7d`, status `SUCCESS`
- Repositorio GitHub conectado: `andreaspsb/Mitologia`
- Branch de auto-deploy: `main`
- Backend auto-deploy validado: deploy `cd31d554-d157-4d56-8478-17a78a1cd561`, status `SUCCESS`
- Frontend auto-deploy validado: deploy `27cd1366-565e-45cc-8805-5a6a3db7fbfa`, status `SUCCESS`

## Regras de ouro

1. Use o Railway CLI pelo WSL, nao pelo Windows nativo.
2. Use explicitamente a distro: `wsl.exe -d Ubuntu`.
3. Sempre carregue o Railway CLI novo com `source ~/.railway/env`.
4. Deploy normal e automatico: commit e push para `origin/main`.
5. Nao publique manualmente direto de `/mnt/c/Users/andre/Repositórios Git/Mitologia`.
6. Se precisar usar `railway up` como fallback, copie o repo para um diretorio nativo do WSL, como `/tmp/mitologia-railway`.
7. Para deploy manual, sempre informe `--service` e `--environment production`.
8. Nunca considere deploy concluido apenas porque ele foi enfileirado; confirme `SUCCESS`.
9. Para logs em automacao, sempre limite a saida com `--lines` e use `--json` quando possivel.

## Auto-deploy via GitHub

O projeto esta configurado para deploy automatico a partir do GitHub.

Backend:

- Service: `mitologia-backend`
- Source: `andreaspsb/Mitologia`
- Branch: `main`
- Root directory: raiz do repositorio
- Builder: `RAILPACK`
- Deploy automatico validado: `cd31d554-d157-4d56-8478-17a78a1cd561`, status `SUCCESS`

Frontend:

- Service: `mitologia-frontend`
- Source: `andreaspsb/Mitologia`
- Branch: `main`
- Root directory: `/frontend`
- Builder: `DOCKERFILE`
- Dockerfile path: `/frontend/Dockerfile`
- Deploy automatico validado: `27cd1366-565e-45cc-8805-5a6a3db7fbfa`, status `SUCCESS`

Fluxo normal:

```powershell
git status
git add .
git commit -m "Describe change"
git push
```

Depois do push, verificar:

```powershell
wsl.exe -d Ubuntu bash -lc "source ~/.railway/env && railway deployment list --project de345e87-0bfc-4e1b-8629-d581eb03f04d --environment production --service mitologia-backend --json"
wsl.exe -d Ubuntu bash -lc "source ~/.railway/env && railway deployment list --project de345e87-0bfc-4e1b-8629-d581eb03f04d --environment production --service mitologia-frontend --json"
```

So considerar publicado quando o deployment mais recente do service afetado estiver em `SUCCESS`.

Observacao importante:

- O primeiro auto-deploy do frontend falhou porque o service estava conectado ao repo sem root directory e Railpack detectou Python na raiz.
- A correcao foi aplicar JSON patch no ambiente para definir `source.rootDirectory=/frontend`, `build.builder=DOCKERFILE` e `build.dockerfilePath=/frontend/Dockerfile`.
- Com GitHub source, o Dockerfile path correto e `/frontend/Dockerfile`; o path `/Dockerfile` funcionava apenas no deploy manual com `railway up frontend --path-as-root`.

## Por que usar WSL nativo, nao `/mnt/c`

Durante o deploy, o Railway CLI criou snapshots corrompidos quando executado diretamente sobre o caminho Windows montado no WSL:

```text
/mnt/c/Users/andre/Repositórios Git/Mitologia
```

Sintoma observado:

- Arquivos raiz como `alembic.ini`, `railpack.json` e `Procfile` chegaram ao Railway como bytes NUL.
- O build falhava mesmo quando os arquivos locais estavam corretos.
- Recriar comandos e variaveis nao resolvia, porque o problema estava no pacote enviado.

Caminho validado:

```bash
rm -rf /tmp/mitologia-railway
mkdir -p /tmp/mitologia-railway
cd "/mnt/c/Users/andre/Repositórios Git/Mitologia"
tar --exclude='.git' \
  --exclude='frontend/node_modules' \
  --exclude='frontend/.next' \
  --exclude='node_modules' \
  --exclude='.pytest_cache' \
  --exclude='__pycache__' \
  --exclude='*.egg-info' \
  -cf - . | tar -C /tmp/mitologia-railway -xf -
cd /tmp/mitologia-railway
file alembic.ini frontend/Dockerfile
```

Resultado esperado:

```text
alembic.ini:         ASCII text
frontend/Dockerfile: ASCII text
```

## Railway CLI no WSL

O CLI antigo instalado no WSL era `4.30.5` e atrapalhou o fluxo. A versao validada foi instalada em:

```text
/home/andreas/.railway/bin/railway
```

Versao validada:

```text
5.23.3
```

Comando de instalacao/atualizacao usado:

```bash
bash <(curl -fsSL https://railway.com/install.sh)
```

Em todos os comandos no Codex/PowerShell, use este formato:

```powershell
wsl.exe -d Ubuntu bash -lc "source ~/.railway/env && railway --version"
```

Se o comando usar o repo:

```powershell
wsl.exe -d Ubuntu bash -lc "source ~/.railway/env && cd /tmp/mitologia-railway && railway status --json"
```

Evite `wsl.exe` sem `-d Ubuntu`; ele ja apresentou comportamento inconsistente neste ambiente.

## Changelog Railway de 2026-07-03

O changelog `#0297 - The peaceful way to ship software, static outbound IPs and IPv6 in the CLI` confirmou pontos importantes para agentes e Codex:

- Railway publicou suporte a hosted MCP nos plugins para Claude Code, Codex, Cursor e Grok.
- Os plugins agora conectam ao hosted MCP server da Railway para setup em um clique; antes configuravam um MCP local via CLI.
- A skill `use-railway` foi atualizada contra Railway CLI `v5.23.3`.
- A skill atualizada deve rotear agentes pelos comandos atuais de config, CDN, WAF e networking do CLI, em vez de fluxos antigos de config patch.
- O CLI ganhou `railway outbound-network` para gerenciar recursos de outbound networking.

Comandos novos citados no changelog:

```bash
railway outbound-network status
railway outbound-network static-ip enable
railway outbound-network static-ip disable
railway outbound-network ipv6 enable
railway outbound-network ipv6 disable
railway outbound-network --help
```

Uso esperado:

- `status` resume static outbound IPs e outbound IPv6 por service/environment.
- `static-ip enable/disable` gerencia IPs IPv4 estaticos de saida; mudancas entram no proximo deploy.
- `ipv6 enable/disable` prepara mudanca de config de ambiente; depois e preciso aplicar/rollout.
- Os comandos aceitam seletores padrao como `--service`, `--environment`, `--project` e `--json`.

Impacto para este projeto:

- Nao muda o deploy atual da Mitologia.
- Reforca que o Railway CLI `5.23.3` e a versao correta para automacao por agente.
- Reforca que, para leituras e acoes de plataforma sem dependencias de arquivos locais, o hosted MCP da Railway deve ser considerado.
- Para `railway up`, snapshot de repo, login local e deploy a partir de arquivos, o CLI no WSL continua sendo o caminho certo.

## Login no Railway

### Caminho preferido

Quando ha browser disponivel na maquina do usuario, o fluxo preferido do Railway e:

```bash
railway login
```

ou, em deploy inicial de app:

```bash
railway up
```

O `railway up` pode autenticar e publicar em um fluxo unico.

### O que aconteceu neste ambiente

No Codex, o login normal nao funcionou bem por falta de TTY/fluxo interativo visivel. O caminho que funcionou foi rodar o login browserless dentro de um pseudo-terminal com `script`:

```powershell
wsl.exe -d Ubuntu bash -lc "cd '/mnt/c/Users/andre/Repositórios Git/Mitologia' && timeout 25s script -q -c 'railway login --browserless' /dev/null"
```

Esse comando imprime um link/codigo. O operador deve abrir o link imediatamente e concluir o login no navegador.

Pontos importantes:

- O codigo expira; se demorar, rode o comando de novo e use o link mais recente.
- Nao rode `railway up --ci` esperando que ele abra login; em modo CI/JSON o Railway nao inicia prompt interativo.
- Depois do login, valide com:

```powershell
wsl.exe -d Ubuntu bash -lc "source ~/.railway/env && railway whoami --json"
```

## Preparar copia nativa do WSL

Sempre antes de deploy:

```powershell
wsl.exe -d Ubuntu bash -lc "rm -rf /tmp/mitologia-railway && mkdir -p /tmp/mitologia-railway && cd '/mnt/c/Users/andre/Repositórios Git/Mitologia' && tar --exclude='.git' --exclude='frontend/node_modules' --exclude='frontend/.next' --exclude='node_modules' --exclude='.pytest_cache' --exclude='__pycache__' --exclude='*.egg-info' -cf - . | tar -C /tmp/mitologia-railway -xf - && cd /tmp/mitologia-railway && file alembic.ini frontend/Dockerfile"
```

Depois linke o projeto:

```powershell
wsl.exe -d Ubuntu bash -lc "source ~/.railway/env && cd /tmp/mitologia-railway && railway link --project de345e87-0bfc-4e1b-8629-d581eb03f04d"
```

## Variaveis do backend

O backend ficou rodando com Railpack, nao com `backend/Dockerfile`.

Variaveis configuradas no service `mitologia-backend`:

```text
DATABASE_URL=${{Postgres.DATABASE_URL}}
BACKEND_CORS_ORIGINS=https://mitologia-frontend-production.up.railway.app
RAILPACK_INSTALL_CMD=pip install --target ./.railway-packages .
RAILPACK_START_CMD=PYTHONPATH=/app/.railway-packages python -c "from alembic.config import main; main()" upgrade head && PYTHONPATH=/app/.railway-packages python scripts/bootstrap_database.py && PYTHONPATH=/app/.railway-packages python -m uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT
```

Por que `PYTHONPATH=/app/.railway-packages`:

- `pip install --target ./.railway-packages .` instala as dependencias em um diretorio local do build.
- No runtime do Railpack, o Python nao encontrou automaticamente essas dependencias.
- Definir `PYTHONPATH` no start command fez Alembic, bootstrap e Uvicorn enxergarem os pacotes.

Por que `python -c "from alembic.config import main; main()" upgrade head`:

- `python -m alembic` falhou porque Alembic nao e executado corretamente assim neste contexto.
- A chamada via `alembic.config.main` funcionou com o `PYTHONPATH` customizado.

Script local para reaplicar as variaveis:

```bash
scripts/railway_set_backend_start.sh
```

Uso:

```powershell
wsl.exe -d Ubuntu bash -lc "source ~/.railway/env && cd /tmp/mitologia-railway && bash scripts/railway_set_backend_start.sh"
```

## Variaveis do frontend

Variavel configurada no service `mitologia-frontend`:

```text
NEXT_PUBLIC_API_BASE_URL=https://mitologia-backend-production.up.railway.app
```

Esse valor precisa ser publico porque o frontend roda no navegador do usuario.

## Deploy do backend

Caminho validado:

```powershell
wsl.exe -d Ubuntu bash -lc "source ~/.railway/env && cd /tmp/mitologia-railway && railway link --project de345e87-0bfc-4e1b-8629-d581eb03f04d && bash scripts/railway_set_backend_start.sh && railway up --service mitologia-backend --environment production --ci --message 'Deploy Mitologia backend from native WSL filesystem'"
```

O deploy validado do backend executou no startup:

1. `alembic upgrade head`
2. `python scripts/bootstrap_database.py`
3. `python -m uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT`

Logs esperados:

```text
Running upgrade -> 20260703_0001
Uvicorn running on http://0.0.0.0:8080
```

Verificacao:

```powershell
wsl.exe -d Ubuntu bash -lc "source ~/.railway/env && cd /tmp/mitologia-railway && railway deployment list --service mitologia-backend --environment production --json"
wsl.exe -d Ubuntu bash -lc "curl -fsS https://mitologia-backend-production.up.railway.app/health"
```

Resposta esperada:

```json
{"status":"ok"}
```

## Deploy do frontend

O frontend usa `frontend/Dockerfile`, mas o deploy deve tratar `frontend` como raiz do snapshot:

```powershell
wsl.exe -d Ubuntu bash -lc "source ~/.railway/env && cd /tmp/mitologia-railway && railway up frontend --path-as-root --service mitologia-frontend --environment production --ci --message 'Deploy Mitologia frontend from native WSL filesystem'"
```

Por isso o `frontend/Dockerfile` deve usar caminhos relativos ao proprio diretorio `frontend`:

```dockerfile
COPY package.json package-lock.json ./
COPY . ./
```

Nao use este formato dentro do Dockerfile quando publicar com `--path-as-root`:

```dockerfile
COPY frontend/package.json frontend/package-lock.json ./
COPY frontend ./
```

Esse formato falhou porque, dentro do snapshot enviado, nao existe uma pasta `frontend`; ela ja virou a raiz.

Verificacao:

```powershell
wsl.exe -d Ubuntu bash -lc "source ~/.railway/env && cd /tmp/mitologia-railway && railway deployment list --service mitologia-frontend --environment production --json"
wsl.exe -d Ubuntu bash -lc "curl -fsS -I https://mitologia-frontend-production.up.railway.app"
wsl.exe -d Ubuntu bash -lc "curl -fsS 'https://mitologia-frontend-production.up.railway.app/search?q=Zeus' | head -c 500"
```

Resultado esperado:

- Deployment mais recente com `"status": "SUCCESS"`.
- HTTP `200` no dominio do frontend.
- HTML servido na rota `/search?q=Zeus`.

## Verificar integracao backend + banco

Smoke test de API:

```powershell
wsl.exe -d Ubuntu bash -lc "curl -fsS 'https://mitologia-backend-production.up.railway.app/search?q=Zeus' | head -c 1000"
```

Resultado esperado:

- JSON com entidades chamadas `Zeus`.
- Presenca de aliases, por exemplo `Júpiter`.
- Se retornar dados, o backend esta acessando o Postgres e o seed rodou.

## Comandos de diagnostico

Listar deployments:

```powershell
wsl.exe -d Ubuntu bash -lc "source ~/.railway/env && cd /tmp/mitologia-railway && railway deployment list --service mitologia-backend --environment production --json"
wsl.exe -d Ubuntu bash -lc "source ~/.railway/env && cd /tmp/mitologia-railway && railway deployment list --service mitologia-frontend --environment production --json"
```

Logs runtime:

```powershell
wsl.exe -d Ubuntu bash -lc "source ~/.railway/env && cd /tmp/mitologia-railway && railway logs --service mitologia-backend --environment production --lines 200 --json"
wsl.exe -d Ubuntu bash -lc "source ~/.railway/env && cd /tmp/mitologia-railway && railway logs --service mitologia-frontend --environment production --lines 200 --json"
```

Logs de build:

```powershell
wsl.exe -d Ubuntu bash -lc "source ~/.railway/env && cd /tmp/mitologia-railway && railway logs --service mitologia-backend --environment production --build --lines 200 --json"
wsl.exe -d Ubuntu bash -lc "source ~/.railway/env && cd /tmp/mitologia-railway && railway logs --service mitologia-frontend --environment production --build --lines 200 --json"
```

Variaveis:

```powershell
wsl.exe -d Ubuntu bash -lc "source ~/.railway/env && cd /tmp/mitologia-railway && railway variable list --service mitologia-backend --environment production --json"
wsl.exe -d Ubuntu bash -lc "source ~/.railway/env && cd /tmp/mitologia-railway && railway variable list --service mitologia-frontend --environment production --json"
```

Dominios:

```powershell
wsl.exe -d Ubuntu bash -lc "source ~/.railway/env && cd /tmp/mitologia-railway && railway domain list --service mitologia-backend --environment production --json"
wsl.exe -d Ubuntu bash -lc "source ~/.railway/env && cd /tmp/mitologia-railway && railway domain list --service mitologia-frontend --environment production --json"
```

## Erros encontrados e resolucoes

### Railway CLI antigo

Sintoma:

- CLI WSL estava em `4.30.5`.
- Login e alguns comandos nao funcionavam como esperado.

Resolucao:

```bash
bash <(curl -fsSL https://railway.com/install.sh)
source ~/.railway/env
railway --version
```

Versao validada: `5.23.3`.

### Login sem TTY

Sintoma:

- `railway login` nao completava bem no Codex.
- O fluxo interativo nao era visivel/confiavel.

Resolucao validada:

```powershell
wsl.exe -d Ubuntu bash -lc "timeout 25s script -q -c 'railway login --browserless' /dev/null"
```

Depois abrir imediatamente o link/codigo exibido.

### `wsl.exe` sem distro explicita

Sintoma:

- Em alguns momentos, `wsl.exe` sem `-d Ubuntu` indicou comportamento inconsistente.

Resolucao:

```powershell
wsl.exe -d Ubuntu bash -lc "..."
```

### Snapshot corrompido a partir de `/mnt/c`

Sintoma:

- Arquivos enviados ao Railway apareciam como NUL bytes.
- `alembic.ini`, `railpack.json` e `Procfile` foram afetados.

Resolucao:

- Copiar repo para `/tmp/mitologia-railway`.
- Conferir `file alembic.ini`.
- Rodar `railway up` dentro de `/tmp/mitologia-railway`.

### Builder Dockerfile do backend nao aplicado

Sintoma:

- Tentativa de mudar builder para Dockerfile nao pegou como esperado.
- `railway environment edit --service-config ... build.builder DOCKERFILE` chegou a retornar "No changes to apply".
- Railpack continuou sendo usado.

Resolucao adotada:

- Aceitar Railpack para o backend.
- Definir `RAILPACK_INSTALL_CMD`.
- Definir `RAILPACK_START_CMD`.
- Instalar dependencias com `pip install --target ./.railway-packages .`.
- Usar `PYTHONPATH=/app/.railway-packages` no start command.

### `$PORT` perdido no start command

Sintoma:

- Start command sem `$PORT` correto, quebrando bind no Railway.

Resolucao:

- Configurar o comando via `--stdin` com heredoc no script `scripts/railway_set_backend_start.sh`.
- Usar aspas que preservem `$PORT` para o runtime do Railway.

### Dependencias Python ausentes no runtime

Sintoma:

- Build instalava, mas runtime nao encontrava pacotes.

Resolucao:

```text
RAILPACK_INSTALL_CMD=pip install --target ./.railway-packages .
PYTHONPATH=/app/.railway-packages ...
```

### Alembic chamado de forma incorreta

Sintoma:

- `python -m alembic` nao funcionou como start step.

Resolucao:

```bash
python -c "from alembic.config import main; main()" upgrade head
```

### Dockerfile do frontend com contexto errado

Sintoma:

```text
"/frontend/package.json": not found
COPY frontend ./ not found
```

Causa:

- Deploy foi feito com `railway up frontend --path-as-root`.
- Logo, o diretorio `frontend` virou raiz do build.
- O Dockerfile ainda esperava que existisse uma subpasta `frontend`.

Resolucao:

- Alterar `frontend/Dockerfile` para copiar `package.json` e `.` da raiz do contexto.

### Deploy reportado cedo demais

Risco:

- `railway up --detach` so confirma que o build foi enfileirado.
- Isso nao significa que a aplicacao esta no ar.

Resolucao:

- Preferir `--ci` quando quiser acompanhar ate o fim.
- Se usar `--detach`, obrigatorio consultar:

```bash
railway deployment list --service <service> --environment production --json
```

So considerar pronto com:

```json
"status": "SUCCESS"
```

## Checklist completo para redeploy

1. Validar localmente se houve mudanca de codigo:

```powershell
C:\Users\andre\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m pytest
cd frontend
npm.cmd run build
```

2. Recriar copia nativa do WSL:

```powershell
wsl.exe -d Ubuntu bash -lc "rm -rf /tmp/mitologia-railway && mkdir -p /tmp/mitologia-railway && cd '/mnt/c/Users/andre/Repositórios Git/Mitologia' && tar --exclude='.git' --exclude='frontend/node_modules' --exclude='frontend/.next' --exclude='node_modules' --exclude='.pytest_cache' --exclude='__pycache__' --exclude='*.egg-info' -cf - . | tar -C /tmp/mitologia-railway -xf - && cd /tmp/mitologia-railway && file alembic.ini frontend/Dockerfile"
```

3. Linkar projeto:

```powershell
wsl.exe -d Ubuntu bash -lc "source ~/.railway/env && cd /tmp/mitologia-railway && railway link --project de345e87-0bfc-4e1b-8629-d581eb03f04d"
```

4. Backend, se necessario:

```powershell
wsl.exe -d Ubuntu bash -lc "source ~/.railway/env && cd /tmp/mitologia-railway && bash scripts/railway_set_backend_start.sh && railway up --service mitologia-backend --environment production --ci --message 'Deploy Mitologia backend from native WSL filesystem'"
```

5. Frontend, se necessario:

```powershell
wsl.exe -d Ubuntu bash -lc "source ~/.railway/env && cd /tmp/mitologia-railway && railway up frontend --path-as-root --service mitologia-frontend --environment production --ci --message 'Deploy Mitologia frontend from native WSL filesystem'"
```

6. Verificar:

```powershell
wsl.exe -d Ubuntu bash -lc "curl -fsS https://mitologia-backend-production.up.railway.app/health"
wsl.exe -d Ubuntu bash -lc "curl -fsS -I https://mitologia-frontend-production.up.railway.app"
wsl.exe -d Ubuntu bash -lc "curl -fsS 'https://mitologia-backend-production.up.railway.app/search?q=Zeus' | head -c 1000"
```

## Quando editar cada coisa

- Mudou backend Python, scripts, Alembic, seed ou modelos: redeploy backend.
- Mudou frontend Next/CSS/componentes: redeploy frontend.
- Mudou variavel `NEXT_PUBLIC_API_BASE_URL`: redeploy frontend, porque ela entra no build.
- Mudou `BACKEND_CORS_ORIGINS`: redeploy/restart backend.
- Mudou o draw.io ou seed: redeploy backend para o bootstrap reprocessar dados no Railway.

## O que nao fazer

- Nao publicar direto de `/mnt/c/...`.
- Nao usar `wsl.exe` sem `-d Ubuntu`.
- Nao assumir que deploy terminou sem `SUCCESS`.
- Nao trocar de volta para SQLite no Railway.
- Nao hardcodar `DATABASE_URL`.
- Nao commitar `.env`.
- Nao usar Dockerfile do frontend com caminhos `frontend/...` se o deploy usa `--path-as-root`.
- Nao remover `PYTHONPATH=/app/.railway-packages` do start command do backend enquanto o backend estiver em Railpack com install target.
