# Backlog

## Fase 1 - POC Local

- [x] Criar dados ficticios financeiros.
- [x] Criar views semanticas.
- [x] Criar catalogo financeiro.
- [x] Criar agente ADK.
- [x] Criar tool BigQuery com validacao.
- [x] Testar perguntas principais via terminal.

## Fase 2 - Google Chat

- [x] Criar adapter HTTP.
- [x] Publicar Cloud Run.
- [x] Criar Google Chat App.
- [x] Testar endpoint `/health` autenticado e depois sem token.
- [x] Testar endpoint `/google-chat` autenticado e depois sem token com payload simulado.
- [x] Liberar invocacao do Cloud Run para o Google Chat.
- [x] Desativar modo Workspace Add-on para usar resposta HTTP comum do Chat.
- [x] Retestar conversa por mensagem direta apos liberacao IAM.
- [x] Corrigir prompt e tool para erro DATE versus STRING em perguntas como "este mes".
- [x] Ajustar adapter para dividir mensagens com multiplas perguntas.
- [x] Criar tool inicial para graficos financeiros.
- [x] Adicionar suporte a graficos com multiplas series.
- [x] Configurar bucket Cloud Storage para graficos.
- [x] Fazer redeploy da correcao de datas, multiplas perguntas e graficos.
- [x] Testar pedidos de grafico no Google Chat.
- [x] Refinar legenda, eixo Y em reais e rotulos dos graficos.
- [ ] Testar conversa em espaco.

## Fase 3 - Governanca

- [ ] Criar tabela de auditoria.
- [ ] Persistir pergunta, SQL, job_id, URL de grafico e tipo de resposta.
- [ ] Criar service account dedicada.
- [ ] Restringir IAM para views especificas.
- [ ] Adicionar validacao do emissor Google Chat.
- [ ] Revisar politica corporativa para endpoint publico e alternativa com validacao forte do emissor.
- [ ] Definir estrategia de acesso aos graficos: bucket publico, URL assinada ou rota autenticada.
- [ ] Criar rotina de limpeza/retencao para PNGs gerados.

## Fase 4 - Producao Controlada

- [ ] Migrar dados ficticios para views gold reais.
- [ ] Homologar metricas com Financeiro.
- [ ] Adicionar testes automatizados de SQL.
- [ ] Adicionar testes automatizados para geracao de graficos.
- [ ] Avaliar Agent Engine como runtime separado.
- [ ] Evoluir resposta de graficos para cards do Google Chat.
- [ ] Adicionar RAG para glossario e politicas financeiras.
- [ ] Expandir para outros dominios.
