CREATE OR REPLACE VIEW `hml-data-clean.poc_financeiro.vw_resultado_mensal` AS
SELECT
  DATE_TRUNC(l.data_lancamento, MONTH) AS mes,
  c.grupo,
  c.categoria,
  SUM(l.valor) AS valor_realizado
FROM `hml-data-clean.poc_financeiro.fato_lancamento_financeiro` l
JOIN `hml-data-clean.poc_financeiro.dim_conta_contabil` c
  ON l.conta_contabil_id = c.conta_contabil_id
GROUP BY mes, c.grupo, c.categoria;

CREATE OR REPLACE VIEW `hml-data-clean.poc_financeiro.vw_despesa_por_centro_custo` AS
SELECT
  DATE_TRUNC(l.data_lancamento, MONTH) AS mes,
  cc.centro_custo,
  cc.area,
  cc.unidade,
  c.categoria,
  SUM(l.valor) AS valor_despesa
FROM `hml-data-clean.poc_financeiro.fato_lancamento_financeiro` l
JOIN `hml-data-clean.poc_financeiro.dim_conta_contabil` c
  ON l.conta_contabil_id = c.conta_contabil_id
JOIN `hml-data-clean.poc_financeiro.dim_centro_custo` cc
  ON l.centro_custo_id = cc.centro_custo_id
WHERE c.grupo = "Despesa"
GROUP BY mes, cc.centro_custo, cc.area, cc.unidade, c.categoria;

CREATE OR REPLACE VIEW `hml-data-clean.poc_financeiro.vw_realizado_vs_orcado` AS
WITH realizado AS (
  SELECT
    DATE_TRUNC(l.data_lancamento, MONTH) AS mes,
    l.centro_custo_id,
    l.conta_contabil_id,
    SUM(l.valor) AS valor_realizado
  FROM `hml-data-clean.poc_financeiro.fato_lancamento_financeiro` l
  GROUP BY mes, l.centro_custo_id, l.conta_contabil_id
),
orcado AS (
  SELECT
    mes_referencia AS mes,
    centro_custo_id,
    conta_contabil_id,
    SUM(valor_orcado) AS valor_orcado
  FROM `hml-data-clean.poc_financeiro.fato_orcamento_financeiro`
  GROUP BY mes, centro_custo_id, conta_contabil_id
)
SELECT
  COALESCE(r.mes, o.mes) AS mes,
  cc.centro_custo,
  cc.area,
  cc.unidade,
  c.grupo,
  c.categoria,
  COALESCE(r.valor_realizado, 0) AS valor_realizado,
  COALESCE(o.valor_orcado, 0) AS valor_orcado,
  COALESCE(r.valor_realizado, 0) - COALESCE(o.valor_orcado, 0) AS variacao_valor
FROM realizado r
FULL OUTER JOIN orcado o
  ON r.mes = o.mes
  AND r.centro_custo_id = o.centro_custo_id
  AND r.conta_contabil_id = o.conta_contabil_id
JOIN `hml-data-clean.poc_financeiro.dim_centro_custo` cc
  ON COALESCE(r.centro_custo_id, o.centro_custo_id) = cc.centro_custo_id
JOIN `hml-data-clean.poc_financeiro.dim_conta_contabil` c
  ON COALESCE(r.conta_contabil_id, o.conta_contabil_id) = c.conta_contabil_id;

CREATE OR REPLACE VIEW `hml-data-clean.poc_financeiro.vw_fornecedores_despesas` AS
SELECT
  DATE_TRUNC(l.data_lancamento, MONTH) AS mes,
  l.parceiro AS fornecedor,
  cc.centro_custo,
  c.categoria,
  SUM(l.valor) AS valor_despesa
FROM `hml-data-clean.poc_financeiro.fato_lancamento_financeiro` l
JOIN `hml-data-clean.poc_financeiro.dim_conta_contabil` c
  ON l.conta_contabil_id = c.conta_contabil_id
JOIN `hml-data-clean.poc_financeiro.dim_centro_custo` cc
  ON l.centro_custo_id = cc.centro_custo_id
WHERE c.grupo = "Despesa"
GROUP BY mes, fornecedor, cc.centro_custo, c.categoria;
