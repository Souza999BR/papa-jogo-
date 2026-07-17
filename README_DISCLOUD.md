# Projeto pronto para Discloud

Arquivos adicionados:
- requirements.txt
- discloud.config
- runtime.txt
- start.sh

## Variáveis de ambiente (Telegram)

O token do bot e o ID do chat/grupo do Telegram NÃO ficam mais escritos no código.
Eles são lidos das variáveis de ambiente `TELEGRAM_TOKEN` e `CHAT_ID`.

### Rodando localmente
1. Copie `.env.example` para `.env`
2. Preencha `TELEGRAM_TOKEN` e `CHAT_ID` com os valores reais
3. O arquivo `.env` nunca deve ser enviado ao GitHub nem a locais públicos (já está no `.gitignore`)

### Rodando na Discloud
A Discloud não deve receber o arquivo `.env` (ele fica de fora do ZIP de deploy, veja abaixo).
Em vez disso, cadastre as variáveis direto no painel da Discloud:
1. Acesse o painel da sua aplicação na Discloud
2. Vá em "Variáveis de Ambiente" (Environment Variables / ENV)
3. Adicione:
   - `TELEGRAM_TOKEN` = token do seu bot
   - `CHAT_ID` = id do grupo/chat
4. Salve e reinicie a aplicação

Assim, mesmo que o código ou o ZIP vazem, o token e o chat_id não ficam expostos.

Como usar:
1. Faça upload deste ZIP na Discloud
2. Cadastre as variáveis de ambiente `TELEGRAM_TOKEN` e `CHAT_ID` no painel (passo acima)
3. Aguarde instalação
4. Inicie a aplicação

