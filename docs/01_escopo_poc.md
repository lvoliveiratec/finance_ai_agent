# Escopo Da POC

## Objetivo

Criar uma POC de agente financeiro que permita consultar dados ficticios no BigQuery usando linguagem natural.

## Dentro Do Escopo

- Dominio financeiro.
- Dados ficticios em `hml-data-clean.poc_financeiro`.
- Tabelas de fatos e dimensoes financeiras.
- Views semanticas para consumo do agente.
- Agente ADK usando Gemini via Vertex AI.
- Tool de BigQuery com validacao de SQL, allowlist de views e dry run.
- Adapter HTTP para Google Chat em Cloud Run.
- Quebra de mensagens com multiplas perguntas.
- Tool de graficos financeiros com PNG salvo em Cloud Storage.
- Graficos simples e comparativos com multiplas series.
- Documentacao tecnica e roteiro de evolucao.

## Fora Do Escopo Inicial

- Dados reais.
- Banco vetorial/RAG.
- Memoria longa dos usuarios.
- Multiplos dominios como RH, Administrativo ou Comercial.
- Fine-tuning de modelo.
- Escrita em tabelas de negocio.
- Acoes transacionais.
- Dashboards completos ou ferramenta de BI substituta.
- Governanca final de compartilhamento de imagens.

## Criterios De Sucesso

- O agente responde perguntas financeiras simples em portugues.
- O agente consulta apenas as views permitidas.
- Toda query passa por validacao antes de executar.
- O agente retorna resultado, filtros e agrupamentos usados.
- A POC funciona no terminal com `adk run`.
- A POC responde pelo Google Chat.
- O agente recusa perguntas fora do dominio financeiro.
- O agente bloqueia pedidos perigosos como apagar, atualizar ou criar tabelas.
- O agente responde multiplas perguntas na mesma mensagem.
- O agente gera graficos financeiros simples e comparativos.

## Perguntas De Demo

- Qual foi a receita realizada por mes?
- Qual foi a despesa por centro de custo?
- Compare realizado versus orcado por mes.
- Quais fornecedores tiveram maior gasto?
- Qual unidade teve maior despesa?
- Quais categorias ficaram acima do orcado?
- Qual foi a receita deste mes?
- Crie um grafico da receita por mes.
- Mostre um grafico comparando realizado versus orcado por mes.
- Crie um grafico de receita e despesa por mes.
