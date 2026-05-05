# Seguranca E Governanca

## Principios

- O agente nao acessa tabelas brutas diretamente na experiencia de negocio.
- O agente consulta apenas views permitidas.
- Toda SQL passa por validacao.
- Toda consulta executa dry run antes da execucao real.
- A POC bloqueia comandos que alteram dados.
- O projeto deve usar service account propria no Cloud Run.

## Validacoes Implementadas

O arquivo `finance_ai_agent/tools/bigquery_tool.py` implementa:

- allowlist de views;
- bloqueio de comandos como `INSERT`, `UPDATE`, `DELETE`, `DROP`, `ALTER`, `CREATE`, `MERGE`;
- obrigatoriedade de referencias com crase;
- limite de bytes processados;
- dry run antes da execucao;
- limite de 50 linhas retornadas para o modelo.
- tratamento estruturado de erros do BigQuery.

O arquivo `finance_ai_agent/tools/chart_tool.py` reutiliza a BigQuery tool para gerar graficos. Assim, os graficos tambem respeitam:

- allowlist de views;
- bloqueio de DDL/DML;
- dry run;
- limite de bytes;
- limite de linhas retornadas.

## IAM Recomendado

Para teste local:

- `roles/aiplatform.user`
- `roles/bigquery.jobUser`
- `roles/bigquery.dataViewer`
- `roles/serviceusage.serviceUsageConsumer`

Para Cloud Run:

- service account dedicada;
- `roles/aiplatform.user`;
- `roles/bigquery.jobUser`;
- permissao de leitura somente no dataset/views da POC.
- permissao de escrita no bucket de graficos, se a capacidade de BI estiver ativa.

## Exposicao Do Cloud Run Na POC

Para integrar rapidamente com Google Chat, a POC usa `allUsers` com `roles/run.invoker` no servico `finance-ai-chat-adapter`.

Isso foi suficiente para validar o fluxo fim a fim, mas nao deve ser o unico controle em producao. Antes de ampliar o uso, adicionar:

- validacao do emissor do evento do Google Chat;
- allowlist de usuarios ou grupos autorizados;
- auditoria persistente de pergunta, SQL e resposta;
- service account dedicada com minimo privilegio;
- revisao da politica corporativa para endpoint publico.

## Exposicao Dos Graficos Na POC

Os graficos sao salvos em Cloud Storage como PNG.

Na POC, o bucket pode ficar legivel publicamente para facilitar a abertura dos links no Google Chat. Para producao, avaliar:

- URLs assinadas com expiracao;
- rota autenticada no Cloud Run para servir imagens;
- bucket privado com controle por identidade;
- politica de retencao e limpeza dos PNGs gerados;
- mascaramento de dados sensiveis antes de gerar imagens.

## Auditoria Recomendada Para Proxima Fase

Criar uma tabela:

```text
hml-data-clean.poc_financeiro.agent_audit_log
```

Campos sugeridos:

- `timestamp`
- `usuario`
- `canal`
- `pergunta`
- `sql_gerado`
- `job_id_bigquery`
- `bytes_estimados`
- `url_grafico`
- `tipo_resposta`
- `status`
- `resumo_resposta`

## Riscos

- O modelo gerar SQL semanticamente incorreto.
- Perguntas ambiguas serem respondidas sem pedir esclarecimento.
- Usuario interpretar dados ficticios como reais.
- Permissao excessiva no projeto ou dataset.
- Endpoint publico sem validacao forte do emissor.
- Bucket publico de graficos sem politica de expiracao.
- Custo de BigQuery se o limite de bytes for removido.
