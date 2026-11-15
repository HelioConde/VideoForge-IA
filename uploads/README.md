# uploads — entrada de arquivos **já existentes** (não gerar imagens)

Pasta de entrada do VideoForge-IA. **Não guardar senhas, tokens ou vídeos oficiais aqui.** Qualquer imagem só deve ser importada mediante SHA-256 e preservada em `canal/<id>/videos/<video-id>/assets/`.

## Dorama Alchemy Lab / C12

Os arquivos abaixo foram produzidos anteriormente e têm registros na biblioteca `/youtube/`, mas os bytes originais ainda não foram anexados a esta conversa nem enviados ao GitHub. **Não há autorização para regenerar ou substituir as imagens.**

| Envie a esta pasta com nome exato | Conteúdo esperado |
|---|---|
| `alchemy-ep01-cinema-3-originais.zip` | Três PNGs RGB da referência cinematográfica (inclui Kael, Elara e confronto no trono) |
| `alchemy-c12-rig-camadas-tecnicas-v2.zip` | Dois fundos técnicos e cinco partes RGBA com transparência real |

A forma mais simples: abra a [pasta uploads no GitHub](https://github.com/HelioConde/VideoForge-IA/tree/main/uploads), clique em **Add file → Upload files**, envie os dois ZIPs originais e confirme o commit na `main`. Podem ser enviados juntos; nenhum arquivo deve ser redimensionado, recriado ou recompactado de forma a alterar os PNGs internos.

1. `qa-alchemy-chat-cinematic-references.yml` importa e verifica os três RGB originais.
2. `import-alchemy-c12-technical-zip.yml` importa e verifica os sete PNGs técnicos por SHA-256.
3. `c12-after-import.yml` recebe a conclusão dos dois importadores, inspeciona a **main**, aguarda se faltar algum arquivo e só então dispara `render-alchemy-c12-three-mesh-technical.yml` por `workflow_dispatch`. Isso evita depender de um `push` do próprio `GITHUB_TOKEN`, que não aciona outro workflow.
4. O render usa os nove arquivos SHA-verificados e produz **prévia técnica de oito segundos** com QA de recomposição neutra e movimento real das malhas. O close dos olhos C12-P01 (quatro segundos) e a aprovação humana continuam pendentes.

Conferir o [checkpoint oficial do episódio](../canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/ESTADO-ATUAL.md) antes de adicionar outros arquivos. Não confundir artifact temporário, referência visual e PNG arquivado na `main`.
