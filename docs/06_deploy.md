# Deploy

## Variaveis

```bash
export PROJECT_ID=hml-data-clean
export REGION=us-central1
export SERVICE_NAME=finance-ai-chat-adapter
export CHARTS_BUCKET=finance-ai-poc-charts-hml-data-clean
export CHARTS_PREFIX=finance-ai-poc/charts
```

## Deploy Cloud Run

Na raiz do projeto:

```bash
bash deploy/deploy_cloud_run.sh
```

O script:

- define o projeto;
- habilita APIs principais;
- publica o servico no Cloud Run;
- configura variaveis de ambiente;
- configura bucket/prefixo para graficos, quando informado;
- deixa o endpoint sem autenticacao para simplificar a POC com Google Chat.

## Bucket Para Graficos

Se a capacidade de BI conversacional estiver ativa, crie um bucket para armazenar PNGs:

```bash
export PROJECT_ID=hml-data-clean
export CHARTS_BUCKET=finance-ai-poc-charts-hml-data-clean

gcloud storage buckets create "gs://${CHARTS_BUCKET}" \
  --project "${PROJECT_ID}" \
  --location US \
  --uniform-bucket-level-access

gcloud storage buckets add-iam-policy-binding "gs://${CHARTS_BUCKET}" \
  --member="allUsers" \
  --role="roles/storage.objectViewer"
```

Para producao, revisar esse acesso publico e considerar URLs assinadas ou rota autenticada.

## Teste Local Do Adapter

Na raiz do projeto:

```bash
python3 -m pip install --user -r chat_adapter/requirements.txt

export GOOGLE_GENAI_USE_VERTEXAI=TRUE
export GOOGLE_CLOUD_PROJECT=hml-data-clean
export GOOGLE_CLOUD_LOCATION=us-central1
export BQ_PROJECT_ID=hml-data-clean
export BQ_DATASET=poc_financeiro
export CHARTS_BUCKET=finance-ai-poc-charts-hml-data-clean
export CHARTS_PREFIX=finance-ai-poc/charts

uvicorn chat_adapter.main:app --host 0.0.0.0 --port 8080
```

Em outro terminal:

```bash
curl -X POST http://localhost:8080/google-chat \
  -H "Content-Type: application/json" \
  --data @tests/payloads/google_chat_message.json
```

## Teste Depois Do Deploy

Depois do deploy, pegue a URL:

```bash
gcloud run services describe finance-ai-chat-adapter \
  --project hml-data-clean \
  --region us-central1 \
  --format='value(status.url)'
```

URL validada:

```text
https://finance-ai-chat-adapter-k5uyvxfr3q-uc.a.run.app
```

Health check sem token apos liberar invocacao publica:

```bash
SERVICE_URL="$(gcloud run services describe finance-ai-chat-adapter \
  --project hml-data-clean \
  --region us-central1 \
  --format='value(status.url)')"

curl "${SERVICE_URL}/health"
```

Resultado esperado:

```json
{"status":"ok"}
```

Teste do endpoint Google Chat com payload simulado:

```bash
SERVICE_URL="$(gcloud run services describe finance-ai-chat-adapter \
  --project hml-data-clean \
  --region us-central1 \
  --format='value(status.url)')"

curl -X POST "${SERVICE_URL}/google-chat" \
  -H "Content-Type: application/json" \
  --data @tests/payloads/google_chat_message.json
```

Se estiver no Cloud Shell e nao tiver o arquivo de payload localmente, use JSON inline ou copie o payload do arquivo `tests/payloads/google_chat_message.json`.

## Permissao De Invocacao

A POC foi validada com invocacao publica do Cloud Run:

```bash
gcloud run services add-iam-policy-binding finance-ai-chat-adapter \
  --project hml-data-clean \
  --region us-central1 \
  --member="allUsers" \
  --role="roles/run.invoker"
```

Sem essa permissao, o Google Chat registra erro `403` no Cloud Run porque nao envia o token de identidade usado nos testes manuais.

Valide sempre sem token depois do deploy:

```bash
curl "${SERVICE_URL}/health"
```

Resultado esperado:

```json
{"status":"ok"}
```

## Correcao De Datas Relativas

Em 2026-05-04 foi identificado um erro para perguntas como:

```text
qual foi a receita deste mes
```

O agente gerou comparacao entre `DATE` e `STRING`. A correcao foi aplicada no prompt e na BigQuery tool para:

- orientar o modelo a usar `DATE 'YYYY-MM-DD'`;
- descobrir o ultimo mes disponivel quando o usuario disser "este mes";
- retornar erro estruturado caso uma SQL invalida escape para a tool.

Depois do redeploy, retestar no Google Chat:

```text
qual foi a receita deste mes
```

## Redeploy Da Capacidade De Graficos

Depois de configurar o bucket, publicar com:

```bash
export CHARTS_BUCKET=finance-ai-poc-charts-hml-data-clean
export CHARTS_PREFIX=finance-ai-poc/charts

bash deploy/deploy_cloud_run.sh
```

Retestar:

```text
Crie um grafico da receita por mes.
Mostre um grafico comparando realizado versus orcado por mes.
Crie um grafico de receita e despesa por mes.
```

Resultados esperados:

- link de imagem PNG;
- legenda amigavel;
- eixo Y em reais;
- graficos comparativos com multiplas series quando aplicavel.

## APIs Necessarias

- Cloud Run API
- Cloud Build API
- Vertex AI API
- BigQuery API
- Google Chat API
- Cloud Storage API

## Observacao Sobre Agent Engine

A POC atual roda o agente dentro do processo do Cloud Run Adapter.

Isso simplifica a primeira entrega. Em uma evolucao, podemos separar:

```text
Google Chat -> Cloud Run Adapter -> Vertex AI Agent Engine -> BigQuery
```

O arquivo `deploy/deploy_agent_engine.py` e um template para essa evolucao.
