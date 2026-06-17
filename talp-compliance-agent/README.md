# TALP Compliance Agent

Agente intermediário de análise de regras de negócio e compliance para o projeto acadêmico **TALP-CIN — Pipeline Multiagente para Validação de User Stories**.

Este repositório implementa o agente:

```text
talp-compliance-agent
```

Ele faz parte de um pipeline multiagente composto por:

1. **talp-invest-agent** — avalia a qualidade da User Story usando critérios INVEST.
2. **talp-compliance-agent** — identifica regras de negócio, compliance, dependências, regras bloqueantes e lacunas.
3. **talp-bdd-agent** — gera ou avalia cenários BDD a partir da User Story enriquecida.

---

## Objetivo

O `talp-compliance-agent` recebe uma User Story já analisada pelo `talp-invest-agent` e executa uma análise de conformidade baseada em catálogo.

O agente identifica:

- regras de negócio aplicáveis;
- regras obrigatórias;
- regras bloqueantes;
- dependências entre regras;
- lacunas de informação;
- requisitos de compliance;
- possibilidade de seguir para o agente BDD.

---

## Restrição principal

O agente **não pode inventar regras**.

Todas as regras utilizadas na análise devem vir exclusivamente do catálogo local:

```text
data/catalog_rules_v1.csv
```

A saída final deve ser rastreável e validada contra esse catálogo.

---

## Pipeline Multiagente

```text
User Story original
        ↓
[talp-invest-agent]
        ↓
Resultado INVEST estruturado
        ↓
[talp-compliance-agent]
        ↓
Análise de regras, compliance, dependências e lacunas
        ↓
[talp-bdd-agent]
        ↓
Cenários BDD / Validação final
```

---

## Estado atual do projeto

Nesta etapa, o projeto já possui:

- API FastAPI funcionando;
- health check;
- catálogo de regras carregado via CSV;
- sincronização do catálogo com banco SQLite;
- persistência de execuções de análise;
- endpoints de análise de compliance;
- endpoint para análise via arquivo JSON;
- Streamlit disponível via Docker;
- Docker Compose validado;
- banco SQLite inicializado automaticamente no startup da API.

---

## Pré-requisitos

Para execução local:

- Python 3.10+ ou 3.11+
- pip
- Git

Para execução com Docker:

- Docker
- Docker Compose

---

## Estrutura do Projeto

```text
talp-compliance-agent/
├── app/
│   ├── api/
│   │   └── routes/
│   │       ├── health.py
│   │       ├── compliance.py
│   │       ├── compliance_runs.py
│   │       └── catalog.py
│   ├── config/
│   │   └── settings.py
│   ├── db/
│   │   ├── base.py
│   │   ├── session.py
│   │   ├── models.py
│   │   └── init_db.py
│   ├── nodes/
│   ├── schemas/
│   │   └── models.py
│   ├── services/
│   │   ├── catalog_repository.py
│   │   ├── file_loader.py
│   │   ├── persistence_service.py
│   │   └── rule_matcher.py
│   ├── graph.py
│   ├── graph_state.py
│   └── main.py
├── data/
│   ├── catalog_rules_v1.csv
│   └── samples/
├── features/
├── prompts/
├── storage/
│   ├── audit/
│   ├── db/
│   ├── exports/
│   └── imports/
├── tests/
├── streamlit_app.py
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
├── .env.example
├── .dockerignore
├── .gitignore
└── README.md
```

---

## Catálogo de Regras

O catálogo principal está em:

```text
data/catalog_rules_v1.csv
```

Regras atuais:

| ID | Nome | Domínio | Obrigatória | Bloqueante |
|---|---|---|---|---|
| RULE_001 | Sinais Vitais Obrigatórios | Triagem | Sim | Sim |
| RULE_002 | Classificação Manchester | Triagem | Sim | Sim |
| RULE_003 | Registro HDA | Atendimento Médico | Sim | Sim |
| RULE_004 | CID Obrigatório | Diagnóstico | Sim | Sim |
| RULE_005 | Conduta Médica Obrigatória | Diagnóstico | Sim | Sim |
| RULE_006 | Atualização de Status | Fluxo Assistencial | Sim | Não |
| RULE_007 | Prescrição Médica Obrigatória | Prescrição | Sim | Sim |
| RULE_008 | Validação CCIH | Controle de Infecção | Sim | Sim |

---

## Execução com Docker

A forma mais simples de subir o projeto é com Docker Compose.

### 1. Subir os containers

```bash
docker compose up --build
```

Caso o usuário ainda não tenha permissão para executar Docker sem `sudo`, use:

```bash
sudo docker compose up --build
```

A API ficará disponível em:

```text
http://localhost:8000
```

O Streamlit ficará disponível em:

```text
http://localhost:8501
```

---

### 2. Testar health check

Em outro terminal:

```bash
curl http://localhost:8000/health
```

Resultado esperado:

```json
{
  "status": "healthy",
  "service": "talp-compliance-agent",
  "version": "0.1.0"
}
```

---

### 3. Acessar documentação da API

Swagger:

```text
http://localhost:8000/docs
```

ReDoc:

```text
http://localhost:8000/redoc
```

---

### 4. Acessar Streamlit

```text
http://localhost:8501
```

---

### 5. Parar os containers

```bash
docker compose down
```

Ou, usando `sudo`:

```bash
sudo docker compose down
```

---

## Execução local sem Docker

### 1. Clonar o repositório

```bash
git clone https://github.com/SEU-USUARIO/talp-compliance-agent.git
cd talp-compliance-agent
```

Substitua `SEU-USUARIO` pelo usuário ou organização real do GitHub.

---

### 2. Criar ambiente virtual

Linux/macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Caso o projeto esteja usando a pasta `venv`:

```bash
python3 -m venv venv
source venv/bin/activate
```

Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

---

### 3. Instalar dependências

```bash
python -m pip install --upgrade pip
pip install -e ".[dev]"
```

Se houver erro com as dependências de desenvolvimento, instalar manualmente:

```bash
pip install fastapi "uvicorn[standard]" pydantic pydantic-settings sqlalchemy pandas odfpy python-dotenv langchain langchain-core langgraph streamlit pytest pytest-bdd httpx ruff
```

---

### 4. Configurar variáveis de ambiente

```bash
cp .env.example .env
```

O `.env` local não deve ser enviado para o Git.

---

### 5. Inicializar banco local

```bash
python -m app.db.init_db
```

O banco SQLite será criado em:

```text
storage/db/compliance_agent.db
```

Esse arquivo também não deve ser enviado para o Git.

---

### 6. Rodar a API localmente

```bash
uvicorn app.main:app --reload
```

Ou:

```bash
python -m uvicorn app.main:app --reload
```

A API ficará disponível em:

```text
http://localhost:8000
```

---

## Endpoints principais

### Health check

```http
GET /health
GET /api/v1/health
```

Exemplo:

```bash
curl http://localhost:8000/health
```

---

### Listar regras do catálogo

```http
GET /api/v1/catalog/rules
```

Exemplo:

```bash
curl http://localhost:8000/api/v1/catalog/rules
```

---

### Sincronizar catálogo com banco

```http
POST /api/v1/catalog/sync
```

Exemplo:

```bash
curl -X POST http://localhost:8000/api/v1/catalog/sync
```

Resultado esperado:

```json
{
  "status": "ok",
  "synced_rules": 8,
  "message": "8 regra(s) sincronizada(s)."
}
```

---

### Executar análise de compliance

```http
POST /api/v1/compliance/analyze
```

Exemplo:

```bash
curl -X POST http://localhost:8000/api/v1/compliance/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "investment_id": "US-001",
    "invest_result": {
      "investment_id": "US-001",
      "status": "warning",
      "criteria_results": [
        {
          "criterion_id": "TEST-001",
          "criterion_name": "Testable",
          "result": true,
          "evidence": "A história possui elementos verificáveis."
        }
      ],
      "summary": "Como médico, quero prescrever antibiótico para paciente internado, para iniciar o tratamento adequado.",
      "metadata": {
        "user_story_text": "Title: Prescricao de antibiotico\n\nComo medico, quero prescrever antibiotico para paciente internado, para iniciar o tratamento adequado.\n\nAcceptance criteria:\n- A prescricao deve ser validada pela CCIH antes da liberacao final"
      }
    }
  }'
```

Resultado esperado: a resposta deve conter regras como `RULE_007` e `RULE_008`, caso a lógica de matching encontre evidências relacionadas a prescrição e antibiótico.

Observações importantes:

- O matching de regras usa preferencialmente `invest_result.metadata.user_story_text` quando esse campo estiver presente.
- Esse campo deve conter a user story renderizada completa, preservando `Title`, `Description`, `Acceptance criteria` e `Additional context` quando existir.
- Na ausência desse campo, o agente usa `invest_result.summary` e complementa a análise com evidências de `criteria_results`.
- Esse comportamento reduz falsos negativos em regras mandatórias quando o resumo do INVEST é curto ou perde keywords relevantes do domínio.

---

### Executar análise a partir de arquivo

```http
POST /api/v1/compliance/analyze-file
```

Exemplo:

```bash
curl -X POST http://localhost:8000/api/v1/compliance/analyze-file \
  -H "Content-Type: application/json" \
  -d '{"file_path": "data/samples/compliance_request_sample.json"}'
```

---

### Listar execuções salvas

```http
GET /api/v1/compliance/runs
```

Exemplo:

```bash
curl http://localhost:8000/api/v1/compliance/runs
```

---

### Consultar execução específica

```http
GET /api/v1/compliance/runs/{run_id}
```

---

## Persistência

O projeto usa SQLite local por padrão.

Configuração no `.env.example`:

```env
DATABASE_URL=sqlite:///./storage/db/compliance_agent.db
```

A aplicação inicializa as tabelas no startup da API.

Arquivos locais de banco e auditoria não são versionados:

```text
storage/db/*.db
storage/audit/*.jsonl
```

As pastas são mantidas no Git por meio de arquivos `.gitkeep`.

---

## Streamlit

A interface Streamlit pode ser executada com Docker Compose:

```bash
docker compose up --build
```

Depois acesse:

```text
http://localhost:8501
```

Também pode ser executada localmente:

```bash
streamlit run streamlit_app.py
```

---

## Testes

Executar todos os testes:

```bash
pytest
```

Executar com detalhes:

```bash
pytest -v
```

Executar testes BDD, se configurados:

```bash
pytest features
```

---

## Docker validado

O Docker Compose foi validado nesta etapa com:

```bash
docker compose up --build
curl http://localhost:8000/health
```

Resultado obtido:

```json
{
  "status": "healthy",
  "service": "talp-compliance-agent",
  "version": "0.1.0"
}
```

Serviços disponíveis:

| Serviço | URL |
|---|---|
| API FastAPI | http://localhost:8000 |
| Swagger | http://localhost:8000/docs |
| ReDoc | http://localhost:8000/redoc |
| Streamlit | http://localhost:8501 |

---

## Como outro desenvolvedor pode revisar

### 1. Clonar o repositório

```bash
git clone https://github.com/SEU-USUARIO/talp-compliance-agent.git
cd talp-compliance-agent
```

### 2. Rodar com Docker

```bash
docker compose up --build
```

### 3. Testar API

```bash
curl http://localhost:8000/health
curl http://localhost:8000/api/v1/catalog/rules
curl -X POST http://localhost:8000/api/v1/catalog/sync
curl http://localhost:8000/api/v1/compliance/runs
```

### 4. Acessar documentação

```text
http://localhost:8000/docs
```

### 5. Acessar Streamlit

```text
http://localhost:8501
```

---

## Problemas comuns

### Erro: porta 8000 em uso

Se aparecer erro de porta ocupada:

```bash
lsof -i :8000
```

Mate o processo:

```bash
kill -9 NUMERO_DO_PID
```

Ou altere a porta externa no `docker-compose.yml`:

```yaml
ports:
  - "8001:8000"
```

Nesse caso, a API ficará em:

```text
http://localhost:8001
```

---

### Erro: permission denied no Docker

Se aparecer:

```text
permission denied while trying to connect to the docker API
```

Use temporariamente:

```bash
sudo docker compose up --build
```

Para corrigir definitivamente:

```bash
sudo usermod -aG docker $USER
```

Depois faça logout/login no Ubuntu.

---

### Aviso: version is obsolete

Se o Docker Compose avisar que `version` é obsoleto, remova a linha:

```yaml
version: "3.8"
```

O arquivo deve começar diretamente com:

```yaml
services:
```

---

## Próximos passos

- [x] Criar estrutura FastAPI.
- [x] Implementar health check.
- [x] Carregar catálogo de regras.
- [x] Criar endpoints de catálogo.
- [x] Sincronizar catálogo com banco SQLite.
- [x] Persistir execuções de análise.
- [x] Criar endpoints de análise.
- [x] Validar execução com Docker Compose.
- [ ] Refinar Streamlit.
- [ ] Adicionar testes BDD finais.
- [ ] Integrar formalmente com saída real do `talp-invest-agent`.
- [ ] Preparar contrato de saída para o `talp-bdd-agent`.
- [ ] Melhorar documentação técnica da arquitetura LangGraph.

---

## Contribuidores

TALP-CIN Team