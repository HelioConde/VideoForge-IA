# Importar as 3 imagens originais de Kael, Elara e da câmera C12-P02

Esta etapa preserva arquivos existentes, sem criar arte. A preferência estética foi aprovada no chat; isso **não** aprova rigs, imagens-mãe por tomada ou MP4.

## Arquivos do ZIP de 7,4 MB

| Nome exato dentro do ZIP | SHA-256 (original) | Uso |
|---|---|---|
| kael-close-salao.png | edb751cdb1c1511e56cd8c8f314a788d9adfb9d4338085cead281efa931ed65f | Referência visual de Kael |
| elara-close-trono.png | bf199f3e3315fc8357e9fdec7e17db47f2a56c6fca6225b7f4983201fc2fcd6a | Referência visual de Elara |
| confronto-trono-c12-p02.png | 01eb7c127b0699d2e502d29dacec0bb39c0e1e23bf8205fdcf6fb70976e70535 | Câmera C12-P02, candidata, não aprovada para render |

Os três PNGs são 941×1672 pixels, em RGB. Não redimensionar, editar ou recomprimir antes de criar o ZIP. O pacote antigo com apenas as duas referências de rosto continua compatível, mas não inclui C12-P02.

## Enviar o pacote

Coloque **alchemy-ep01-cinema-3-originais.zip** no caminho **uploads/alchemy-ep01-cinema-3-originais.zip**, na branch main do GitHub HelioConde/VideoForge-IA.

Uma alternativa no Windows é usar o script [enviar-referencias-cinema.ps1](../../../../scripts/enviar-referencias-cinema.ps1) do repositório, apontando o parâmetro ZipPath para o ZIP baixado no chat. O script verifica os três hashes antes do git push, não exige tokens no arquivo e não altera os originais.

O [workflow de referências](https://github.com/HelioConde/VideoForge-IA/actions/workflows/qa-alchemy-chat-cinematic-references.yml) dispara automaticamente. Ele confere nomes, tamanhos, SHA-256, formato PNG, CRC e resolução, recusa entradas extras ou arquivos adulterados e arquiva apenas os bytes originais em:

- assets/referencias/chat-aprovadas/kael-close-salao.png
- assets/referencias/chat-aprovadas/elara-close-trono.png
- assets/referencias/chat-aprovadas/confronto-trono-c12-p02.png

Em seguida salva **qa-referencias-chat-cinematograficas.json**. Exigir a confirmação ORIGINAL_EXACT_SHA_VERIFIED nos dois closes e EXACT_SOURCE_ARCHIVED na câmera C12. O ZIP de três fontes será preferido automaticamente quando presente.

## Separar arquivamento de aprovação visual

Os originais arquivados passam a ser **referências rastreáveis**, não automaticamente 36 imagens-mãe específicas. C12-P02 ainda requer revisão visual da posição e do olhar da princesa, mesmo com seu SHA correto. A história não deve revelar sua identidade antes da C12. Continuam obrigatórios recortes RGBA por câmera, fundo reconstruído, rig, pivôs, underlays e QA humano.

Manter o lock SEM-GERACAO-NOVAS-IMAGENS.lock; preservar os 71 PNGs legados e as 14 mães antigas. Nenhum novo PNG, render MP4 ou upload ao YouTube é liberado por esta importação.
