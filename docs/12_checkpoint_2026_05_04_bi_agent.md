# Checkpoint 2026-05-04 - BI Agent

## Resumo

A POC evoluiu de agente financeiro textual para uma primeira versao de BI conversacional.

Fluxo validado:

```text
Google Chat -> Cloud Run -> ADK Agent -> BigQuery -> Chart Tool -> Cloud Storage -> Google Chat
```

## O Que Foi Implementado

- Tool `criar_grafico_financeiro`.
- Geração de PNG com `matplotlib`.
- Upload dos graficos no Cloud Storage.
- Resposta no Google Chat com link do PNG.
- Suporte a graficos simples com uma metrica.
- Suporte a graficos comparativos com multiplas series.
- Legendas amigaveis nos graficos.
- Eixo Y formatado em reais.
- Quebra de mensagens com multiplas perguntas.
- Refinos de prompt para sinonimos e perguntas de negocio.

## Graficos Validados

Perguntas testadas:

```text
Crie um grafico da receita por mes.
Gere um grafico de barras da despesa por centro de custo.
Mostre um grafico comparando realizado versus orcado por mes.
Crie um grafico de receita e despesa por mes.
Quero um grafico dos fornecedores com maior gasto.
```

Resultados:

- graficos de linha para evolucao temporal;
- graficos de barra para rankings;
- duas series para realizado versus orcado;
- duas series para receita versus despesa;
- links de PNG abertos corretamente a partir do Google Chat.

## Arquivos Alterados

- `finance_ai_agent/tools/chart_tool.py`
- `finance_ai_agent/agent.py`
- `chat_adapter/main.py`
- `chat_adapter/requirements.txt`
- `requirements.txt`
- `deploy/deploy_cloud_run.sh`
- `docs/11_graficos_bi_agent.md`

## Configuracao Usada

```bash
export CHARTS_BUCKET=finance-ai-poc-charts-hml-data-clean
export CHARTS_PREFIX=finance-ai-poc/charts
```

## Estado Atual

Validado:

- Google Chat respondendo;
- BigQuery consultado com SQL controlado;
- multiplas perguntas respondidas separadamente;
- datas relativas tratadas;
- graficos gerados e publicados;
- graficos comparativos com multiplas series;
- bloqueio de comandos perigosos;
- recusa para perguntas fora do dominio financeiro.

Pendencias para piloto governado:

- auditoria persistente;
- service account dedicada;
- validacao forte do emissor Google Chat;
- revisao da exposicao publica do endpoint e do bucket;
- politica de retencao dos PNGs;
- cards do Google Chat para exibir graficos com melhor experiencia.
