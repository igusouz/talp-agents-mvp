# talp-invest-agent

Agente deterministico para avaliar user stories segundo INVEST.

O fluxo segue um grafo fixo:

1. Validacao da entrada.
2. Carregamento de prompts versionados.
3. Analise INVEST estruturada.
4. Guardrails agentic de evidencia literal e conteudo permitido.
5. Classificacao deterministica.
6. Relatorio condicional para historias ruins.
7. Validacao do output final.
8. Log de auditoria em JSONL.

## Regras principais

- A classificacao final nao e decidida pelo LLM.
- `boa`: todos os criterios INVEST passam.
- `ruim`: pelo menos um criterio INVEST falha.
- Evidencias devem existir literalmente no texto da user story.
- O relatorio so aparece para user stories classificadas como `ruim`.
- O relatorio nao recomenda melhorias e nao reescreve a user story.
- Logs ficam em arquivo; nenhum banco de dados e usado.
- Logs registram versao, hash, template e prompt renderizado usado em cada execucao.

## Padrao agentic guardrails

O padrao de guardrails foi implementado como controle antes e depois do uso do
modelo:

- Entrada: rejeita user story vazia ou fora do limite definido no schema.
- Analise INVEST: remove evidencias que nao aparecem literalmente na entrada.
- Analise INVEST: transforma `pass` sem evidencia literal em `fail`.
- Classificacao: usa regra deterministica em codigo, nao decisao livre do LLM.
- Relatorio: aceita apenas criterios que falharam.
- Relatorio: rejeita evidencia nao literal.
- Relatorio: bloqueia linguagem de recomendacao ou reescrita.
- Fallback: se o relatorio violar os guardrails, um relatorio deterministico e gerado a partir da analise validada.

## Outros padrões agentic

- Workflow agent
- Reflection / critique controlada
- Planning explícito
- Tool use restrito
- Structured output
- Human-auditable trace

## Execucao

```powershell
uv run --extra dev pytest
$env:GOOGLE_API_KEY="..."
uv run talp-invest-agent "Como cliente, quero redefinir minha senha para recuperar acesso a minha conta."
```

Para desenvolvimento sem chamada externa ao modelo:

```powershell
uv run talp-invest-agent --backend heuristic "Como administrador, quero melhorar o sistema."
```

O backend `heuristic` existe para testes locais e regressao. O backend padrao e `llm`.

## Execucao com Docker

Construa a imagem:

```powershell
docker build -t talp-invest-agent .
```

Execute sem chamada externa ao modelo:

```powershell
docker run --rm talp-invest-agent --backend heuristic "Como administrador, quero melhorar o sistema."
```

Execute com LLM usando variaveis de ambiente:

```powershell
docker run --rm --env-file .env -v "${PWD}/logs:/app/logs" talp-invest-agent "Como cliente, quero redefinir minha senha para recuperar acesso a minha conta."
```

Em Linux/macOS, use a forma equivalente para montar os logs:

```bash
docker run --rm --env-file .env -v "$(pwd)/logs:/app/logs" talp-invest-agent "Como cliente, quero redefinir minha senha para recuperar acesso a minha conta."
```

Use `.env.example` como referencia para criar um arquivo `.env` local. O volume
em `/app/logs` preserva os arquivos de auditoria gerados pelo container.

## Variaveis de ambiente

```text
GOOGLE_API_KEY
GEMINI_API_KEY
TALP_LLM_MODEL=gemini-2.5-flash
TALP_AUDIT_LOG_DIR=logs/audit
```

`GOOGLE_API_KEY` e a variavel preferida pelo pacote LangChain Google GenAI.
`GEMINI_API_KEY` tambem e aceita pelo agente como alias.
