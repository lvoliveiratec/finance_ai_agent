SELECT
  mes,
  SUM(valor_realizado) AS receita_realizada
FROM `hml-data-clean.poc_financeiro.vw_resultado_mensal`
WHERE grupo = "Receita"
GROUP BY mes
ORDER BY mes;

SELECT
  centro_custo,
  SUM(valor_despesa) AS despesa_realizada
FROM `hml-data-clean.poc_financeiro.vw_despesa_por_centro_custo`
GROUP BY centro_custo
ORDER BY despesa_realizada DESC;

SELECT
  mes,
  SUM(valor_realizado) AS valor_realizado,
  SUM(valor_orcado) AS valor_orcado,
  SUM(variacao_valor) AS variacao_valor
FROM `hml-data-clean.poc_financeiro.vw_realizado_vs_orcado`
GROUP BY mes
ORDER BY mes;

SELECT
  fornecedor,
  SUM(valor_despesa) AS valor_despesa
FROM `hml-data-clean.poc_financeiro.vw_fornecedores_despesas`
GROUP BY fornecedor
ORDER BY valor_despesa DESC;
