# Importação de imagens já geradas na conversa

Esta pasta só existe para receber o ZIP **já existente** criado nesta conversa. **Não criar nem gerar imagens novas.**

1. Baixe o arquivo fornecido na conversa com nome `alchemy-lab-imagens-geradas-anteriormente.zip`.
2. Pelo GitHub, acesse esta pasta e use **Add file > Upload files** para enviar o ZIP com esse nome exato, fazendo commit em `main`.
3. O workflow [import-alchemy-existing-chat-assets.yml](../../../../../.github/workflows/import-alchemy-existing-chat-assets.yml) verificará o manifesto e SHA de oito PNGs, copiará os arquivos existentes para `../assets/cena-01/variacoes-geradas-na-conversa/`, registrará QA como candidato **não aprovado** e excluirá o ZIP intermediário do Git.
4. Não repetir o upload se os oito PNGs já tiverem sido importados. Não usar essas imagens como rig sem validação de geometria, perspectiva e origem.

Este importador não invoca modelos de IA, não desenha partes novas, não gera MP4 e não publica nada no YouTube.
