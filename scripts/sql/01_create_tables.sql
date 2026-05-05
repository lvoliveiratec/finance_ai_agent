CREATE SCHEMA IF NOT EXISTS `hml-data-clean.poc_financeiro`
OPTIONS(location = "US");

CREATE OR REPLACE TABLE `hml-data-clean.poc_financeiro.dim_centro_custo` AS
SELECT * FROM UNNEST([
  STRUCT("CC001" AS centro_custo_id, "Financeiro" AS centro_custo, "Administrativo" AS area, "Sao Paulo" AS unidade),
  STRUCT("CC002", "Recursos Humanos", "Administrativo", "Sao Paulo"),
  STRUCT("CC003", "Comercial", "Receita", "Rio de Janeiro"),
  STRUCT("CC004", "Operacoes", "Operacional", "Curitiba"),
  STRUCT("CC005", "Tecnologia", "Administrativo", "Belo Horizonte")
]);

CREATE OR REPLACE TABLE `hml-data-clean.poc_financeiro.dim_conta_contabil` AS
SELECT * FROM UNNEST([
  STRUCT("4001" AS conta_contabil_id, "Receita de Servicos" AS conta_contabil, "Receita" AS grupo, "Receita Operacional" AS categoria),
  STRUCT("4002", "Receita de Produtos", "Receita", "Receita Operacional"),
  STRUCT("5001", "Salarios e Encargos", "Despesa", "Pessoal"),
  STRUCT("5002", "Fornecedores Terceiros", "Despesa", "Servicos Terceiros"),
  STRUCT("5003", "Marketing e Vendas", "Despesa", "Comercial"),
  STRUCT("5004", "Infraestrutura e Sistemas", "Despesa", "Tecnologia"),
  STRUCT("5005", "Aluguel e Condominio", "Despesa", "Administrativo")
]);

CREATE OR REPLACE TABLE `hml-data-clean.poc_financeiro.fato_lancamento_financeiro` AS
SELECT * FROM UNNEST([
  STRUCT(DATE "2026-01-05" AS data_lancamento, "L001" AS lancamento_id, "CC003" AS centro_custo_id, "4001" AS conta_contabil_id, "Cliente Alpha" AS parceiro, "RECEITA" AS tipo_lancamento, CAST(185000.00 AS NUMERIC) AS valor),
  STRUCT(DATE "2026-01-12", "L002", "CC003", "4002", "Cliente Beta", "RECEITA", CAST(92000.00 AS NUMERIC)),
  STRUCT(DATE "2026-01-15", "L003", "CC001", "5001", "Folha Interna", "DESPESA", CAST(42000.00 AS NUMERIC)),
  STRUCT(DATE "2026-01-18", "L004", "CC002", "5001", "Folha Interna", "DESPESA", CAST(58000.00 AS NUMERIC)),
  STRUCT(DATE "2026-01-20", "L005", "CC005", "5004", "Cloud Provider X", "DESPESA", CAST(31500.00 AS NUMERIC)),
  STRUCT(DATE "2026-01-25", "L006", "CC003", "5003", "Agencia Criativa", "DESPESA", CAST(27000.00 AS NUMERIC)),
  STRUCT(DATE "2026-02-04", "L007", "CC003", "4001", "Cliente Alpha", "RECEITA", CAST(198000.00 AS NUMERIC)),
  STRUCT(DATE "2026-02-10", "L008", "CC003", "4002", "Cliente Gama", "RECEITA", CAST(110000.00 AS NUMERIC)),
  STRUCT(DATE "2026-02-14", "L009", "CC001", "5001", "Folha Interna", "DESPESA", CAST(43500.00 AS NUMERIC)),
  STRUCT(DATE "2026-02-17", "L010", "CC004", "5002", "Fornecedor Logistica", "DESPESA", CAST(49000.00 AS NUMERIC)),
  STRUCT(DATE "2026-02-21", "L011", "CC005", "5004", "Cloud Provider X", "DESPESA", CAST(35200.00 AS NUMERIC)),
  STRUCT(DATE "2026-02-26", "L012", "CC003", "5003", "Agencia Criativa", "DESPESA", CAST(31000.00 AS NUMERIC)),
  STRUCT(DATE "2026-03-03", "L013", "CC003", "4001", "Cliente Delta", "RECEITA", CAST(212000.00 AS NUMERIC)),
  STRUCT(DATE "2026-03-09", "L014", "CC003", "4002", "Cliente Beta", "RECEITA", CAST(97000.00 AS NUMERIC)),
  STRUCT(DATE "2026-03-13", "L015", "CC001", "5001", "Folha Interna", "DESPESA", CAST(44800.00 AS NUMERIC)),
  STRUCT(DATE "2026-03-16", "L016", "CC002", "5002", "Consultoria RH", "DESPESA", CAST(22000.00 AS NUMERIC)),
  STRUCT(DATE "2026-03-20", "L017", "CC005", "5004", "Cloud Provider X", "DESPESA", CAST(38900.00 AS NUMERIC)),
  STRUCT(DATE "2026-03-24", "L018", "CC004", "5005", "Administradora Predial", "DESPESA", CAST(18000.00 AS NUMERIC)),
  STRUCT(DATE "2026-04-05", "L019", "CC003", "4001", "Cliente Alpha", "RECEITA", CAST(225000.00 AS NUMERIC)),
  STRUCT(DATE "2026-04-11", "L020", "CC003", "4002", "Cliente Gama", "RECEITA", CAST(125000.00 AS NUMERIC)),
  STRUCT(DATE "2026-04-15", "L021", "CC001", "5001", "Folha Interna", "DESPESA", CAST(45500.00 AS NUMERIC)),
  STRUCT(DATE "2026-04-19", "L022", "CC004", "5002", "Fornecedor Logistica", "DESPESA", CAST(52000.00 AS NUMERIC)),
  STRUCT(DATE "2026-04-23", "L023", "CC005", "5004", "Cloud Provider X", "DESPESA", CAST(41000.00 AS NUMERIC)),
  STRUCT(DATE "2026-04-27", "L024", "CC003", "5003", "Agencia Criativa", "DESPESA", CAST(36500.00 AS NUMERIC))
]);

CREATE OR REPLACE TABLE `hml-data-clean.poc_financeiro.fato_orcamento_financeiro` AS
SELECT * FROM UNNEST([
  STRUCT(DATE "2026-01-01" AS mes_referencia, "CC003" AS centro_custo_id, "4001" AS conta_contabil_id, CAST(180000.00 AS NUMERIC) AS valor_orcado),
  STRUCT(DATE "2026-01-01", "CC003", "4002", CAST(95000.00 AS NUMERIC)),
  STRUCT(DATE "2026-01-01", "CC001", "5001", CAST(40000.00 AS NUMERIC)),
  STRUCT(DATE "2026-01-01", "CC002", "5001", CAST(56000.00 AS NUMERIC)),
  STRUCT(DATE "2026-01-01", "CC005", "5004", CAST(30000.00 AS NUMERIC)),
  STRUCT(DATE "2026-01-01", "CC003", "5003", CAST(25000.00 AS NUMERIC)),
  STRUCT(DATE "2026-02-01", "CC003", "4001", CAST(195000.00 AS NUMERIC)),
  STRUCT(DATE "2026-02-01", "CC003", "4002", CAST(105000.00 AS NUMERIC)),
  STRUCT(DATE "2026-02-01", "CC001", "5001", CAST(42000.00 AS NUMERIC)),
  STRUCT(DATE "2026-02-01", "CC004", "5002", CAST(46000.00 AS NUMERIC)),
  STRUCT(DATE "2026-02-01", "CC005", "5004", CAST(34000.00 AS NUMERIC)),
  STRUCT(DATE "2026-02-01", "CC003", "5003", CAST(30000.00 AS NUMERIC)),
  STRUCT(DATE "2026-03-01", "CC003", "4001", CAST(205000.00 AS NUMERIC)),
  STRUCT(DATE "2026-03-01", "CC003", "4002", CAST(100000.00 AS NUMERIC)),
  STRUCT(DATE "2026-03-01", "CC001", "5001", CAST(44000.00 AS NUMERIC)),
  STRUCT(DATE "2026-03-01", "CC002", "5002", CAST(20000.00 AS NUMERIC)),
  STRUCT(DATE "2026-03-01", "CC005", "5004", CAST(37000.00 AS NUMERIC)),
  STRUCT(DATE "2026-03-01", "CC004", "5005", CAST(18000.00 AS NUMERIC)),
  STRUCT(DATE "2026-04-01", "CC003", "4001", CAST(220000.00 AS NUMERIC)),
  STRUCT(DATE "2026-04-01", "CC003", "4002", CAST(115000.00 AS NUMERIC)),
  STRUCT(DATE "2026-04-01", "CC001", "5001", CAST(45000.00 AS NUMERIC)),
  STRUCT(DATE "2026-04-01", "CC004", "5002", CAST(50000.00 AS NUMERIC)),
  STRUCT(DATE "2026-04-01", "CC005", "5004", CAST(39000.00 AS NUMERIC)),
  STRUCT(DATE "2026-04-01", "CC003", "5003", CAST(34000.00 AS NUMERIC))
]);
