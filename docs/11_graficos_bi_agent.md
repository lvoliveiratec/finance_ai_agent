# Graficos E BI Agent

## Objetivo

Adicionar uma capacidade inicial de BI conversacional na POC.

Status: validado no Google Chat em 2026-05-04.

Fluxo:

```text
Usuario pede grafico
-> Google Chat
-> Cloud Run Adapter
-> ADK Agent
-> BigQuery
-> Chart Tool
-> Cloud Storage
-> resposta com link do PNG
```

## Tool Criada

Arquivo:

```text
finance_ai_agent/tools/chart_tool.py
```

Tool:

```text
criar_grafico_financeiro
```

Ela:

- executa SQL segura usando a mesma validacao da BigQuery tool;
- gera PNG com `matplotlib`;
- salva o arquivo no Cloud Storage;
- retorna a URL do grafico para o Google Chat.
- suporta graficos simples com `eixo_y`;
- suporta graficos comparativos com `eixos_y`, por exemplo realizado versus orcado.
- formata eixo Y e rotulos monetarios em reais;
- troca nomes tecnicos de campos por nomes amigaveis na legenda, como `valor_realizado` para `Realizado`.

## Variaveis De Ambiente

```bash
export CHARTS_BUCKET=finance-ai-poc-charts-hml-data-clean
export CHARTS_PREFIX=finance-ai-poc/charts
```

Opcional:

```bash
export CHARTS_PUBLIC_BASE_URL=https://storage.googleapis.com/finance-ai-poc-charts-hml-data-clean
```

## Criar Bucket Para A POC

Sugestao para ambiente de homologacao:

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

Esse acesso publico simplifica a visualizacao no Google Chat. Para producao, revisar a politica de exposicao e considerar URLs assinadas ou uma rota autenticada no proprio Cloud Run.

## Permissoes Do Cloud Run

A service account do Cloud Run precisa conseguir gravar objetos no bucket.

Para a POC:

```bash
gcloud storage buckets add-iam-policy-binding "gs://${CHARTS_BUCKET}" \
  --member="serviceAccount:SERVICE_ACCOUNT_DO_CLOUD_RUN" \
  --role="roles/storage.objectCreator"
```

Se o Cloud Run estiver usando a service account padrao do Compute, confirme o e-mail dela no detalhe do servico Cloud Run.

## Exemplos De Perguntas

```text
Crie um grafico da receita por mes.
Gere um grafico de barras da despesa por centro de custo.
Mostre um grafico comparando realizado versus orcado por mes.
Quero um grafico dos fornecedores com maior gasto.
Crie um grafico de receita e despesa por mes.
```

## Testes Validados

Foram validados no Google Chat:

- grafico de linha da receita realizada por mes;
- grafico de barras de despesa por centro de custo;
- grafico de barras de fornecedores com maior gasto;
- grafico de linha com multiplas series para realizado versus orcado;
- grafico de linha com multiplas series para receita versus despesa.

Refinamentos aplicados:

- legenda amigavel;
- eixo Y formatado em reais;
- eixo X com nomes amigaveis;
- labels monetarios controlados para reduzir poluicao visual.

## Exemplos De Uso Da Tool

Grafico simples:

```text
eixo_x: mes
eixo_y: receita_realizada
tipo: linha
```

Grafico com multiplas series:

```text
eixo_x: mes
eixos_y:
  - valor_realizado
  - valor_orcado
tipo: linha
```

Para rankings, usar `tipo: barra`. Para evolucao mensal e comparativos por tempo, usar `tipo: linha`.

Aliases recomendados para SQL de graficos:

```text
valor_realizado -> Realizado
valor_orcado -> Orçado
receita_realizada -> Receita
despesa_realizada -> Despesa
valor_despesa -> Despesa
total_gasto -> Gasto
```

## Limitacoes Da Primeira Versao

- Resposta volta com link do PNG, nao com card rico.
- Bucket precisa estar acessivel para o Google Chat abrir a imagem.
- Graficos suportados: linha, barra simples e barra agrupada para multiplas series.
- A tool usa no maximo as linhas retornadas pela consulta segura.

## Proximos Passos

- Evoluir resposta para cards do Google Chat.
- Avaliar URLs assinadas ou rota autenticada para acesso aos PNGs.
- Criar politica de retencao e limpeza dos graficos.
- Adicionar testes automatizados para geracao de graficos.
- Registrar URL do grafico na auditoria persistente.
