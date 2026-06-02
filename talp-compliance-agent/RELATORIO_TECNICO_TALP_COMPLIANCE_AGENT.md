# Relatório Técnico — TALP Compliance Agent

## 1. Visão geral do projeto

O projeto desenvolvido até aqui se chama:

```text
talp-compliance-agent
```

Ele faz parte de um projeto acadêmico maior chamado:

```text
Pipeline Multiagente para Validação de User Stories
```

Esse pipeline usa agentes de software para analisar e enriquecer histórias de usuário antes que elas sejam usadas para gerar cenários BDD, testes ou documentação.

Uma **User Story** é uma forma simples de descrever uma funcionalidade esperada em um sistema.

Exemplo:

```text
Como médico, quero prescrever antibiótico para paciente internado,
para iniciar o tratamento adequado.
```

O objetivo do pipeline é fazer com que essa User Story passe por diferentes agentes, cada um com uma responsabilidade específica.

---

## 2. Onde o `talp-compliance-agent` fica no pipeline

O sistema possui três agentes principais:

```text
┌──────────────────────┐
│  talp-invest-agent   │
│  Agente 1            │
│                      │
│  Avalia qualidade    │
│  da User Story       │
│  usando INVEST       │
└──────────┬───────────┘
           │
           │ Resultado INVEST estruturado
           ▼
┌──────────────────────────┐
│ talp-compliance-agent    │
│ Agente 2                 │
│                          │
│ Identifica regras de     │
│ negócio, compliance,     │
│ dependências, bloqueios  │
│ e lacunas                │
└──────────┬───────────────┘
           │
           │ User Story enriquecida
           │ com análise de compliance
           ▼
┌──────────────────────┐
│  talp-bdd-agent      │
│  Agente 3            │
│                      │
│  Gera ou avalia      │
│  cenários BDD        │
└──────────────────────┘
```

O agente desenvolvido neste repositório é o **Agente 2**, ou seja, o agente intermediário.

Ele não cria a User Story e também não gera os cenários BDD finais. A função dele é analisar a história de usuário já qualificada pelo Agente 1 e verificar quais regras de negócio ou compliance precisam ser consideradas antes de seguir para o Agente 3.

---

## 3. O que cada agente faz

### 3.1. Agente 1 — `talp-invest-agent`

O primeiro agente analisa a qualidade da User Story usando os critérios INVEST.

INVEST significa:

| Critério | Significado |
|---|---|
| I | Independent / Independente |
| N | Negotiable / Negociável |
| V | Valuable / Valiosa |
| E | Estimable / Estimável |
| S | Small / Pequena |
| T | Testable / Testável |

Exemplo de análise do Agente 1:

```json
{
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
  "metadata": {}
}
```

Esse resultado é enviado para o `talp-compliance-agent`.

---

### 3.2. Agente 2 — `talp-compliance-agent`

Este é o projeto atual.

Ele recebe o resultado do Agente 1 e procura identificar:

- regras de negócio aplicáveis;
- regras obrigatórias;
- regras bloqueantes;
- dependências;
- requisitos de compliance;
- lacunas de informação;
- possibilidade de seguir para o Agente BDD.

A restrição mais importante é:

```text
O agente não pode inventar regras.
```

Todas as regras precisam existir previamente em um catálogo local.

---

### 3.3. Agente 3 — `talp-bdd-agent`

O terceiro agente recebe a User Story já analisada e enriquecida, para então trabalhar com cenários BDD.

BDD significa **Behavior Driven Development**, ou Desenvolvimento Orientado por Comportamento.

Um exemplo de cenário BDD seria:

```gherkin
Cenário: Prescrever antibiótico para paciente internado
  Dado que o paciente está internado
  Quando o médico prescreve um antibiótico
  Então o sistema deve verificar a necessidade de validação CCIH
```

---

## 4. Escopo do `talp-compliance-agent`

O escopo atual do agente é:

```text
Receber uma User Story analisada pelo Agente INVEST
+
Consultar um catálogo de regras
+
Detectar regras aplicáveis
+
Identificar lacunas e dependências
+
Persistir a execução
+
Disponibilizar resultado via API e Docker
```

Ele ainda não é o sistema final completo, mas já possui uma base funcional importante.

---

## 5. O que o agente recebe

O agente recebe um JSON com o resultado do `talp-invest-agent`.

Exemplo:

```json
{
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
    "metadata": {}
  }
}
```

Neste formato:

- `investment_id` identifica a análise ou User Story;
- `invest_result` contém o resultado vindo do Agente 1;
- `summary` contém o texto da User Story;
- `criteria_results` contém os critérios INVEST avaliados.

---

## 6. Como o agente recebe os dados

Atualmente, o agente consegue receber dados de duas formas.

---

### 6.1. Via JSON direto na API

Endpoint:

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
      "metadata": {}
    }
  }'
```

---

### 6.2. Via arquivo JSON local

Endpoint:

```http
POST /api/v1/compliance/analyze-file
```

Exemplo:

```bash
curl -X POST http://localhost:8000/api/v1/compliance/analyze-file \
  -H "Content-Type: application/json" \
  -d '{"file_path": "data/samples/compliance_request_sample.json"}'
```

Esse endpoint é importante porque no futuro o Agente 1 poderá exportar um arquivo JSON, e o Agente 2 poderá ler esse arquivo.

---

## 7. O que o agente entrega

O agente entrega uma análise de compliance contendo:

- identificador da análise;
- regras detectadas;
- regras obrigatórias;
- regras bloqueantes;
- lacunas;
- dependências;
- metadados;
- indicação se pode seguir para o BDD.

Exemplo conceitual de saída:

```json
{
  "analysis_id": "uuid-da-execucao",
  "investment_id": "US-001",
  "rules_detected": [
    {
      "rule_id": "RULE_007",
      "name": "Prescrição Médica Obrigatória",
      "domain": "Prescrição",
      "blocking": true
    },
    {
      "rule_id": "RULE_008",
      "name": "Validação CCIH",
      "domain": "Controle de Infecção",
      "blocking": true
    }
  ],
  "gaps": [],
  "dependencies": [],
  "metadata": {
    "can_continue_to_bdd": true
  }
}
```

A estrutura exata pode variar conforme os schemas atuais do projeto, mas a ideia é essa.

---

## 8. Recurso visual — funcionamento interno do agente

```text
Entrada
│
│
├── JSON vindo do talp-invest-agent
│   └── Contém User Story + avaliação INVEST
│
▼
┌──────────────────────────────┐
│ 1. Receber requisição         │
│    FastAPI                   │
└───────────────┬──────────────┘
                │
                ▼
┌──────────────────────────────┐
│ 2. Ler resultado INVEST       │
│    User Story vem no summary │
└───────────────┬──────────────┘
                │
                ▼
┌──────────────────────────────┐
│ 3. Carregar catálogo          │
│    data/catalog_rules_v1.csv │
└───────────────┬──────────────┘
                │
                ▼
┌──────────────────────────────┐
│ 4. Procurar regras aplicáveis │
│    por palavras-chave         │
└───────────────┬──────────────┘
                │
                ▼
┌──────────────────────────────┐
│ 5. Identificar dependências   │
│    e lacunas                  │
└───────────────┬──────────────┘
                │
                ▼
┌──────────────────────────────┐
│ 6. Salvar execução no banco   │
│    SQLite                     │
└───────────────┬──────────────┘
                │
                ▼
Saída
│
└── JSON com análise de compliance
```

---

## 9. Catálogo de regras usado pelo agente

O catálogo principal está no arquivo:

```text
data/catalog_rules_v1.csv
```

Ele contém as regras que o agente pode usar.

Atualmente existem 8 regras:

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

Exemplo:

Se a User Story contém:

```text
prescrever antibiótico
```

O agente pode detectar:

```text
RULE_007 — Prescrição Médica Obrigatória
RULE_008 — Validação CCIH
```

Porque essas regras existem no catálogo.

---

## 10. Por que o agente não pode inventar regras

Essa é uma exigência central do projeto.

O agente não deve fazer isso:

```text
"A história fala de antibiótico, então vou criar uma nova regra chamada
RULE_999 - Autorização Especial de Farmácia."
```

Isso seria errado, porque `RULE_999` não existe no catálogo.

O comportamento correto é:

```text
A história fala de antibiótico.
No catálogo existe RULE_008 relacionada a antibiótico e CCIH.
Então o agente pode retornar RULE_008.
```

Essa restrição melhora:

- rastreabilidade;
- confiabilidade;
- explicabilidade;
- avaliação acadêmica;
- integração futura com os outros agentes.

---

## 11. Estrutura atual do projeto

A estrutura do projeto até esta etapa é aproximadamente:

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

## 12. Principais tecnologias usadas

### 12.1. Python

Linguagem principal do projeto.

---

### 12.2. FastAPI

Framework usado para criar a API.

É ele que disponibiliza endpoints como:

```text
/health
/api/v1/catalog/rules
/api/v1/compliance/analyze
```

---

### 12.3. Pydantic

Usado para validar os dados de entrada e saída.

Exemplo: garantir que o JSON enviado para a API tem os campos esperados.

---

### 12.4. SQLAlchemy

Usado para trabalhar com banco de dados.

Atualmente o projeto usa SQLite.

---

### 12.5. SQLite

Banco de dados local usado para salvar:

- execuções de análise;
- regras sincronizadas do catálogo.

---

### 12.6. Docker

Usado para rodar o projeto de forma padronizada sem precisar configurar tudo manualmente na máquina.

---

### 12.7. Docker Compose

Usado para subir mais de um serviço ao mesmo tempo:

- API FastAPI;
- Streamlit.

---

### 12.8. Streamlit

Interface visual simples para interagir com o agente.

Está disponível em:

```text
http://localhost:8501
```

---

## 13. Banco de dados

O projeto já cria um banco SQLite local.

Caminho:

```text
storage/db/compliance_agent.db
```

Esse banco armazena as execuções feitas pelo agente.

Importante:

```text
O banco local não deve ser enviado para o Git.
```

Por isso, ele fica ignorado no `.gitignore`.

O projeto mantém apenas a pasta `storage/db/` por meio de um arquivo `.gitkeep`.

---

## 14. Endpoints implementados

### 14.1. Health check

```http
GET /health
GET /api/v1/health
```

Serve para verificar se a API está funcionando.

Exemplo:

```bash
curl http://localhost:8000/health
```

Resposta validada:

```json
{
  "status": "healthy",
  "service": "talp-compliance-agent",
  "version": "0.1.0"
}
```

---

### 14.2. Listar regras do catálogo

```http
GET /api/v1/catalog/rules
```

Serve para listar as regras conhecidas pelo agente.

Exemplo:

```bash
curl http://localhost:8000/api/v1/catalog/rules
```

---

### 14.3. Sincronizar catálogo com banco

```http
POST /api/v1/catalog/sync
```

Serve para copiar as regras do CSV para o banco SQLite.

Exemplo:

```bash
curl -X POST http://localhost:8000/api/v1/catalog/sync
```

Resposta esperada:

```json
{
  "status": "ok",
  "synced_rules": 8,
  "message": "8 regra(s) sincronizada(s)."
}
```

---

### 14.4. Executar análise de compliance

```http
POST /api/v1/compliance/analyze
```

Recebe um JSON direto e executa a análise.

---

### 14.5. Executar análise por arquivo

```http
POST /api/v1/compliance/analyze-file
```

Recebe o caminho de um arquivo JSON local e executa a análise.

---

### 14.6. Listar execuções salvas

```http
GET /api/v1/compliance/runs
```

Lista análises que já foram executadas e persistidas no banco.

---

### 14.7. Consultar execução específica

```http
GET /api/v1/compliance/runs/{run_id}
```

Busca uma execução pelo identificador.

---

## 15. O que foi feito até aqui

### 15.1. Estrutura inicial do projeto

Foi criada a estrutura base do repositório `talp-compliance-agent`.

A estrutura foi pensada para manter consistência com os outros agentes:

- organização em `app/`;
- rotas em `app/api/routes/`;
- serviços em `app/services/`;
- schemas em `app/schemas/`;
- banco em `app/db/`;
- arquivos de dados em `data/`;
- armazenamento local em `storage/`.

---

### 15.2. API FastAPI funcionando

A API foi configurada em:

```text
app/main.py
```

Ela registra os routers principais:

- health;
- compliance;
- compliance runs;
- catalog.

Também inicializa o banco no startup da aplicação.

---

### 15.3. Health check validado

Foi validado que o endpoint:

```text
GET /health
```

responde corretamente.

Resposta obtida:

```json
{
  "status": "healthy",
  "service": "talp-compliance-agent",
  "version": "0.1.0"
}
```

---

### 15.4. Catálogo de regras configurado

Foi configurado o catálogo:

```text
data/catalog_rules_v1.csv
```

Esse catálogo contém as regras V1 do projeto.

---

### 15.5. Endpoints de catálogo criados

Foram criados os endpoints:

```text
GET /api/v1/catalog/rules
POST /api/v1/catalog/sync
```

Eles permitem:

- listar regras;
- sincronizar regras do CSV para o banco.

---

### 15.6. Persistência em banco SQLite

Foi implementado suporte a banco SQLite com SQLAlchemy.

O banco é inicializado com:

```bash
python -m app.db.init_db
```

Ou automaticamente quando a API sobe.

---

### 15.7. Execuções de análise persistidas

O endpoint de análise agora salva a execução no banco.

Isso permite consultar depois quais análises foram feitas.

---

### 15.8. Endpoints de análise criados

Foram criados ou ajustados:

```text
POST /api/v1/compliance/analyze
POST /api/v1/compliance/analyze-file
GET /api/v1/compliance/runs
GET /api/v1/compliance/runs/{run_id}
```

---

### 15.9. Docker validado

O projeto foi validado com Docker Compose.

Comando executado:

```bash
docker compose up --build
```

Serviços iniciados:

- `talp-compliance-agent-api`;
- `talp-compliance-agent-streamlit`.

Log validado:

```text
Application startup complete.
```

Health check validado:

```bash
curl http://localhost:8000/health
```

Resposta:

```json
{
  "status": "healthy",
  "service": "talp-compliance-agent",
  "version": "0.1.0"
}
```

---

### 15.10. Streamlit subindo no Docker

O Streamlit subiu e ficou disponível em:

```text
http://localhost:8501
```

---

### 15.11. README atualizado

O README foi atualizado para substituir o contexto errado de “investimentos” pelo contexto real do projeto:

```text
Pipeline Multiagente para Validação de User Stories
```

Também foram incluídas instruções para rodar com Docker.

---

## 16. Como executar o projeto com Docker

Essa é a forma mais simples para outro colega rodar.

### 16.1. Clonar o repositório

```bash
git clone https://github.com/SEU-USUARIO/talp-compliance-agent.git
cd talp-compliance-agent
```

---

### 16.2. Subir com Docker

```bash
docker compose up --build
```

Se der erro de permissão:

```bash
sudo docker compose up --build
```

---

### 16.3. Testar se a API está funcionando

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

### 16.4. Abrir documentação da API

```text
http://localhost:8000/docs
```

---

### 16.5. Abrir Streamlit

```text
http://localhost:8501
```

---

## 17. Como executar localmente sem Docker

### 17.1. Clonar repositório

```bash
git clone https://github.com/SEU-USUARIO/talp-compliance-agent.git
cd talp-compliance-agent
```

---

### 17.2. Criar ambiente virtual

```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

### 17.3. Instalar dependências

```bash
python -m pip install --upgrade pip
pip install -e ".[dev]"
```

---

### 17.4. Criar `.env`

```bash
cp .env.example .env
```

---

### 17.5. Inicializar banco

```bash
python -m app.db.init_db
```

---

### 17.6. Rodar API

```bash
uvicorn app.main:app --reload
```

---

### 17.7. Testar

```bash
curl http://localhost:8000/health
```

---

## 18. Como outro desenvolvedor pode revisar

A pessoa revisora deve fazer:

```bash
git clone https://github.com/SEU-USUARIO/talp-compliance-agent.git
cd talp-compliance-agent
docker compose up --build
```

Depois testar:

```bash
curl http://localhost:8000/health
curl http://localhost:8000/api/v1/catalog/rules
curl -X POST http://localhost:8000/api/v1/catalog/sync
curl http://localhost:8000/api/v1/compliance/runs
```

E abrir no navegador:

```text
http://localhost:8000/docs
http://localhost:8501
```

---

## 19. Situação do Git até aqui

A branch usada no desenvolvimento desta etapa é:

```text
fix/parte-17-endpoints-persistence
```

Foram feitas alterações em arquivos como:

```text
Dockerfile
docker-compose.yml
README.md
.dockerignore
app/main.py
app/api/routes/catalog.py
app/api/routes/compliance.py
app/api/routes/compliance_runs.py
app/services/persistence_service.py
```

A versão local ficou à frente da remota porque foram feitas alterações depois do último push.

O próximo passo recomendado foi:

```bash
git add Dockerfile README.md docker-compose.yml .dockerignore
git commit -m "docs: update README and validate docker setup"
git push -u origin fix/parte-17-endpoints-persistence
```

---

## 20. Problemas encontrados e resolvidos

### 20.1. Porta 8000 ocupada

Erro encontrado:

```text
ERROR: [Errno 98] Address already in use
```

Significado:

```text
Já havia outro processo usando a porta 8000.
```

Solução:

```bash
lsof -i :8000
kill -9 NUMERO_DO_PID
```

Ou usar outra porta temporária.

---

### 20.2. Docker sem permissão

Erro encontrado:

```text
permission denied while trying to connect to the docker API
```

Solução temporária:

```bash
sudo docker compose up --build
```

Solução definitiva:

```bash
sudo usermod -aG docker $USER
```

Depois fazer logout/login no Ubuntu.

---

### 20.3. Docker Compose com aviso de version obsoleta

Aviso:

```text
the attribute version is obsolete
```

Solução:

Remover a linha:

```yaml
version: "3.8"
```

O arquivo deve começar por:

```yaml
services:
```

---

## 21. Pontos de atenção para continuidade

Ainda há pontos que precisam ser refinados depois.

---

### 21.1. Streamlit

O Streamlit já sobe no Docker, mas ainda precisa ser revisado funcionalmente.

Próximo trabalho:

- melhorar interface;
- permitir colar JSON;
- permitir executar análise;
- mostrar regras detectadas;
- permitir baixar resultado JSON.

---

### 21.2. Testes

Ainda precisa consolidar os testes:

- testes unitários;
- testes de API;
- testes BDD;
- validação do catálogo;
- validação da saída.

---

### 21.3. Integração real com o `talp-invest-agent`

Hoje o agente já aceita JSON em formato compatível, mas ainda precisa ser validado com a saída real final do Agente 1.

---

### 21.4. Contrato para o `talp-bdd-agent`

Ainda precisa ser fechado o contrato de saída que será consumido pelo Agente 3.

---

### 21.5. LangGraph

A estrutura do projeto já prevê uma arquitetura agentic, mas o fluxo ainda pode ser refinado para usar LangGraph de forma mais formal.

---

## 22. Resumo executivo

O `talp-compliance-agent` já possui uma base funcional.

Ele:

```text
Recebe resultado do Agente 1
        ↓
Lê a User Story
        ↓
Consulta catálogo de regras
        ↓
Identifica regras aplicáveis
        ↓
Salva execução no banco
        ↓
Entrega resultado via API
```

O projeto já roda com Docker:

```bash
docker compose up --build
```

A API responde corretamente:

```bash
curl http://localhost:8000/health
```

Resposta validada:

```json
{
  "status": "healthy",
  "service": "talp-compliance-agent",
  "version": "0.1.0"
}
```

A documentação Swagger fica em:

```text
http://localhost:8000/docs
```

O Streamlit fica em:

```text
http://localhost:8501
```

A etapa atual concluiu a base de:

- API;
- catálogo;
- persistência;
- endpoints;
- Docker;
- README.

O próximo passo recomendado é terminar de subir essa versão para o GitHub e depois continuar com o refinamento do Streamlit, testes e integração real com os agentes 1 e 3.
