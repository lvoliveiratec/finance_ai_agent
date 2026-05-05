# Google Chat

## Papel Do Google Chat

O Google Chat sera a interface de conversa para usuarios de negocio.

Fluxo:

```text
Usuario envia mensagem -> Google Chat App -> Cloud Run -> Agente -> BigQuery/Cloud Storage -> Resposta
```

## Criar O App

1. Acesse o Google Cloud Console.
2. Entre no projeto `hml-data-clean`.
3. Habilite a Google Chat API.
4. Acesse a configuracao da Google Chat API.
5. Crie um Chat App.
6. Configure o endpoint HTTP com a URL do Cloud Run.
7. Permita mensagens diretas e/ou espacos.
8. Publique para usuarios de teste.

## Endpoint

Endpoint atual do Cloud Run:

```text
https://finance-ai-chat-adapter-k5uyvxfr3q-uc.a.run.app/
```

Use esta URL na configuracao do Google Chat App:

```text
https://finance-ai-chat-adapter-k5uyvxfr3q-uc.a.run.app/google-chat
```

## Configuracao Usada Na POC

```text
App name: Finance AI POC
Connection settings: HTTP endpoint URL
Endpoint: https://finance-ai-chat-adapter-k5uyvxfr3q-uc.a.run.app/google-chat
Visibility: usuarios de teste no dominio
Workspace Add-on: desativado
```

Funcionalidades recomendadas:

- receber mensagens 1:1;
- permitir entrada em espacos, se a POC precisar testar em salas;
- registrar erros em Cloud Logging.

## Status Atual

O fluxo fim a fim foi validado em 2026-05-04:

```text
Google Chat -> Cloud Run -> ADK Agent -> BigQuery -> Google Chat
```

O app respondeu corretamente no Google Chat para:

```text
Qual foi a receita realizada por mes?
```

Pontos que precisaram ser ajustados:

- `roles/run.invoker` para `allUsers` no Cloud Run, permitindo chamada do Google Chat;
- modo Workspace Add-on desativado, pois a POC usa resposta HTTP simples no formato `{"text": "..."}`;
- prompt e tool ajustados para tratar campos `DATE` corretamente em perguntas como "este mes".
- adapter ajustado para dividir multiplas perguntas em uma mensagem;
- tool de graficos adicionada para retornar links de PNG no Cloud Storage.

Capacidades validadas:

- perguntas financeiras textuais;
- perguntas com datas relativas;
- multiplas perguntas na mesma mensagem;
- recusas para assuntos fora do dominio financeiro;
- bloqueio de comandos perigosos;
- graficos simples;
- graficos comparativos com multiplas series.

## Testes Validados

Health check sem token depois da liberacao publica:

```bash
curl "https://finance-ai-chat-adapter-k5uyvxfr3q-uc.a.run.app/health"
```

Resultado:

```json
{"status":"ok"}
```

Teste do fluxo completo com payload simulado:

```bash
SERVICE_URL="https://finance-ai-chat-adapter-k5uyvxfr3q-uc.a.run.app"

curl -X POST "${SERVICE_URL}/google-chat" \
  -H "Content-Type: application/json" \
  --data '{
    "type": "MESSAGE",
    "message": {
      "text": "Qual foi a receita realizada por mes?",
      "argumentText": "Qual foi a receita realizada por mes?",
      "sender": {
        "name": "users/test-user",
        "email": "usuario.teste@empresa.com"
      },
      "space": {
        "name": "spaces/test-space"
      },
      "thread": {
        "name": "spaces/test-space/threads/test-thread"
      }
    },
    "space": {
      "name": "spaces/test-space"
    },
    "user": {
      "name": "users/test-user",
      "email": "usuario.teste@empresa.com"
    }
  }'
```

Resultado esperado:

```json
{
  "text": "A receita realizada por mes foi..."
}
```

Teste real no Google Chat:

```text
Usuario: Qual foi a receita realizada por mes?
Finance AI POC: A receita realizada foi...
```

Teste de graficos:

```text
Mostre um grafico comparando realizado versus orcado por mes.
Crie um grafico de receita e despesa por mes.
```

Resultado esperado:

- resposta textual curta;
- link para PNG no Cloud Storage;
- grafico com legenda amigavel e eixo em reais.

## Permissao Cloud Run

A permissao publica de invocacao foi aplicada com:

```bash
gcloud run services add-iam-policy-binding finance-ai-chat-adapter \
  --project hml-data-clean \
  --region us-central1 \
  --member="allUsers" \
  --role="roles/run.invoker"
```

Esse caminho foi usado para a POC porque o Google Chat precisa chamar o endpoint HTTP do Cloud Run sem enviar o token manual usado nos testes via `curl`.

Alternativa pelo Console:

```text
Cloud Run > finance-ai-chat-adapter > Permissions > Grant access
Principal: allUsers
Role: Cloud Run Invoker
```

## Configuracao Importante Do Google Chat

Para esta POC, o app deve ficar configurado como Chat App HTTP comum.

Deixar desmarcado:

```text
Criar este app do Chat como um complemento do Workspace
```

Se essa opcao ficar marcada, o Google Chat passa a esperar respostas de add-on/card, e pode mostrar:

```text
Finance AI POC nao esta respondendo
```

mesmo quando o Cloud Run retorna `200`.

## Eventos Tratados

O adapter trata:

- `ADDED_TO_SPACE`;
- mensagens comuns com `message.text`;
- argumentos de slash command com `message.argumentText`.

Quando uma mensagem contem varias perguntas em linhas separadas, o adapter chama o agente separadamente para cada pergunta e consolida a resposta em blocos numerados.

## Limitacoes Da POC

- Sessao em memoria local do container.
- Sem persistencia de historico entre reinicios do Cloud Run.
- Sem validacao criptografica explicita do emissor do evento.
- Cloud Run esta publico para simplificar a integracao inicial com Google Chat.
- Links de graficos usam Cloud Storage e precisam de politica de acesso adequada.

Para producao, adicionar verificacao de autenticidade do Google Chat, persistencia de sessao, revisao de exposicao publica do endpoint e estrategia de acesso para graficos.
