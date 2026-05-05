# POC Financeiro AI

POC de um agente financeiro conversacional usando Google ADK, Vertex AI, BigQuery, Google Chat, Cloud Run e Cloud Storage.

## Objetivo

Permitir que areas de negocio consultem indicadores financeiros em linguagem natural, com execucao controlada em BigQuery.

Esta primeira versao cobre:

- dominio Financeiro;
- dados ficticios no BigQuery;
- agente ADK com Gemini via Vertex AI;
- ferramenta segura de consulta BigQuery;
- validacao de SQL;
- scripts para criar tabelas e views;
- adaptador HTTP para Google Chat em Cloud Run;
- geracao de graficos PNG com Cloud Storage;
- respostas com multiplas perguntas na mesma mensagem;
- inicio de um agente de BI conversacional;
- documentacao tecnica e roteiro da POC.

## Arquitetura

Diagrama visual:

```text
docs/architecture_flow.svg
```

```text
Google Chat
  -> Cloud Run Chat Adapter
    -> ADK Agent
      -> Vertex AI Gemini
      -> BigQuery Tool -> SQL validator + dry run -> BigQuery
      -> Chart Tool -> Cloud Storage
  <- resposta textual ou link de grafico PNG
```

Para a primeira validacao local, o fluxo e:

```text
adk run finance_ai_agent -> Vertex AI -> BigQuery
```

## Estrutura

```text
poc_financeiro/
  finance_ai_agent/          # Agente ADK
  chat_adapter/              # Endpoint HTTP para Google Chat
  scripts/sql/               # Criacao dos dados ficticios e views
  deploy/                    # Scripts de deploy
  docs/                      # Desenhos, escopo, seguranca e operacao
  presentations/             # Deck executivo da POC
  requirements.txt           # Dependencias para teste local do agente
```

## Setup Local

```bash
python3 -m pip install --user -r requirements.txt

export GOOGLE_GENAI_USE_VERTEXAI=TRUE
export GOOGLE_CLOUD_PROJECT=hml-data-clean
export GOOGLE_CLOUD_LOCATION=us-central1
export BQ_PROJECT_ID=hml-data-clean
export BQ_DATASET=poc_financeiro
export CHARTS_BUCKET=finance-ai-poc-charts-hml-data-clean
export CHARTS_PREFIX=finance-ai-poc/charts
```

Autenticacao:

```bash
gcloud auth application-default login
gcloud config set project hml-data-clean
gcloud auth application-default set-quota-project hml-data-clean
```

Rodar agente:

```bash
adk run finance_ai_agent
```

Perguntas para teste:

```text
Qual foi a receita realizada por mes?
Qual foi a despesa por centro de custo?
Compare realizado versus orcado por mes.
Quais fornecedores tiveram maior gasto?
Qual foi a receita deste mes?
Crie um grafico da receita por mes.
Mostre um grafico comparando realizado versus orcado por mes.
```

## Criar Dados Ficticios

Rode os scripts em ordem:

```bash
bq query --use_legacy_sql=false --project_id=hml-data-clean < scripts/sql/01_create_tables.sql
bq query --use_legacy_sql=false --project_id=hml-data-clean < scripts/sql/02_create_views.sql
bq query --use_legacy_sql=false --project_id=hml-data-clean < scripts/sql/03_validation_queries.sql
```

## Proximos Passos

1. Criar auditoria persistente em BigQuery para pergunta, SQL, job_id e URL de grafico.
2. Criar service account dedicada para o Cloud Run com minimo privilegio.
3. Adicionar validacao forte do emissor Google Chat.
4. Avaliar URLs assinadas ou rota autenticada para graficos em vez de bucket publico.
5. Evoluir resposta visual para cards do Google Chat.
6. Migrar a execucao do agente para Vertex AI Agent Engine, se desejado.
7. Substituir dados ficticios por views gold certificadas.
8. Expandir para outros dominios de negocio.

## Status Atual

Data do checkpoint: 2026-05-04.

Concluido:

- agente local validado com `adk run`;
- BigQuery validado com dados ficticios;
- Cloud Run deployado;
- endpoint `/health` validado sem token apos liberacao publica;
- endpoint `/google-chat` validado com payload simulado sem token;
- Google Chat App criado como `Finance AI POC`;
- fluxo Google Chat fim a fim validado apos desativar o modo Workspace Add-on e liberar invocacao publica do Cloud Run;
- correcao de datas relativas e tratamento de erro BigQuery aplicada no codigo;
- adapter ajustado para quebrar mensagens com multiplas perguntas e consultar uma pergunta por vez;
- tool inicial de graficos financeiros adicionada para evoluir a POC para BI conversacional;
- graficos simples e comparativos com multiplas series validados no Google Chat;
- bucket Cloud Storage configurado para publicar PNGs da POC;
- refinamentos visuais aplicados nos graficos: legenda amigavel, eixo Y em reais e rotulos controlados.

Pendente:

- criar auditoria persistente em BigQuery.
- criar service account dedicada e revisar IAM;
- adicionar validacao forte do emissor Google Chat;
- avaliar cards do Google Chat para exibir graficos de forma mais rica.

URL atual do Cloud Run:

```text
https://finance-ai-chat-adapter-k5uyvxfr3q-uc.a.run.app
```

Endpoint configurado no Google Chat:

```text
https://finance-ai-chat-adapter-k5uyvxfr3q-uc.a.run.app/google-chat
```

Checkpoint mais recente:

```text
docs/12_checkpoint_2026_05_04_bi_agent.md
```

## Apresentacao Executiva

Deck da POC:

```text
presentations/finance-ai-poc-exa.pptx
```

Resumo do deck:

- contexto EXA;
- problema e tese da POC;
- arquitetura Google Chat + Cloud Run + ADK + Vertex AI + BigQuery;
- funcionamento do agente;
- governanca de SQL;
- BI conversacional com graficos;
- status atual do Google Chat e ajustes de acesso;
- roadmap para piloto governado.
