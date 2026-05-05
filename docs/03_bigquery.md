# BigQuery

## Projeto E Dataset

```text
Projeto: hml-data-clean
Dataset: poc_financeiro
Location: US
```

## Tabelas

### dim_centro_custo

Dimensao de centro de custo.

Campos:

- `centro_custo_id`
- `centro_custo`
- `area`
- `unidade`

### dim_conta_contabil

Dimensao de contas contabeis.

Campos:

- `conta_contabil_id`
- `conta_contabil`
- `grupo`
- `categoria`

### fato_lancamento_financeiro

Lancamentos realizados de receita e despesa.

Campos:

- `data_lancamento`
- `lancamento_id`
- `centro_custo_id`
- `conta_contabil_id`
- `parceiro`
- `tipo_lancamento`
- `valor`

### fato_orcamento_financeiro

Valores orcados por mes, centro de custo e conta contabil.

Campos:

- `mes_referencia`
- `centro_custo_id`
- `conta_contabil_id`
- `valor_orcado`

## Views Semanticas

### vw_resultado_mensal

Usada para receita, despesa e resultado por mes.

### vw_despesa_por_centro_custo

Usada para analises de despesa por centro de custo, area, unidade e categoria.

### vw_realizado_vs_orcado

Usada para comparativos entre realizado e orcado.

Tambem alimenta graficos comparativos com multiplas series, como:

- `valor_realizado`
- `valor_orcado`
- `variacao_valor`

### vw_fornecedores_despesas

Usada para ranking e analise de fornecedores.

Tambem alimenta graficos de barras para maiores gastos por fornecedor.

## Uso Pelos Graficos

A tool de graficos usa as mesmas views permitidas e passa pela mesma validacao da BigQuery tool.

Exemplos de aliases recomendados para SQLs de grafico:

- `receita_realizada`
- `despesa_realizada`
- `valor_realizado`
- `valor_orcado`
- `valor_despesa`
- `total_gasto`

## Ordem De Criacao

```bash
bq query --use_legacy_sql=false --project_id=hml-data-clean < scripts/sql/01_create_tables.sql
bq query --use_legacy_sql=false --project_id=hml-data-clean < scripts/sql/02_create_views.sql
bq query --use_legacy_sql=false --project_id=hml-data-clean < scripts/sql/03_validation_queries.sql
```
