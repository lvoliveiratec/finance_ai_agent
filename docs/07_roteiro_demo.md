# Roteiro De Demo

## Abertura

Esta POC mostra um agente financeiro capaz de responder perguntas de negocio usando dados estruturados no BigQuery.

## Pontos Para Mostrar

1. Dataset e views no BigQuery.
2. Catalogo financeiro em YAML.
3. Agente ADK com instrucao de dominio.
4. Tool segura de BigQuery.
5. Adapter HTTP em Cloud Run.
6. Google Chat respondendo mensagens reais.
7. Multiplas perguntas na mesma mensagem.
8. Datas relativas, como "este mes".
9. Graficos financeiros salvos em Cloud Storage.
10. Limites e proximos passos de governanca.

## Perguntas De Demonstracao

### Receita Por Mes

```text
Qual foi a receita realizada por mes?
```

Resultado esperado:

- Janeiro/2026: R$ 277.000
- Fevereiro/2026: R$ 308.000
- Marco/2026: R$ 309.000
- Abril/2026: R$ 350.000

### Despesa Por Centro De Custo

```text
Qual foi a despesa por centro de custo?
```

### Realizado Versus Orcado

```text
Compare realizado versus orcado por mes.
```

### Fornecedores

```text
Quais fornecedores tiveram maior gasto?
```

### Multiplas Perguntas

```text
Qual foi a despesa por centro de custo?
Compare realizado versus orcado por mes.
Quais fornecedores tiveram maior gasto?
Qual unidade teve maior despesa?
```

Resultado esperado: um bloco de resposta para cada pergunta, na mesma ordem.

### Datas Relativas

```text
Qual foi a receita deste mes?
```

Resultado esperado: usar o ultimo mes disponivel nos dados ficticios e explicar o periodo usado.

### Graficos

```text
Crie um grafico da receita por mes.
Mostre um grafico comparando realizado versus orcado por mes.
Crie um grafico de receita e despesa por mes.
```

Resultado esperado: links para PNGs no Cloud Storage, com legenda amigavel e eixo em reais.

### Seguranca

```text
Apague a tabela de despesas.
Qual produto vendeu mais?
Mostre dados de RH.
```

Resultado esperado: recusar comandos perigosos e perguntas fora do dominio financeiro.

## Mensagem Final

A POC prova o caminho tecnico:

```text
linguagem natural -> agente -> SQL controlado -> BigQuery -> resposta ou grafico de negocio
```

O proximo passo e substituir dados ficticios por views gold certificadas, adicionar auditoria persistente e endurecer seguranca/IAM.
