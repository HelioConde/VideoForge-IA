# C12 — MP4 técnico por rig Three.js + Remotion

**Estado:** aguardando importação de bytes originais do chat. **Não é o episódio oficial.** A revisão visual e a reconstrução de regiões ocultas ainda estão pendentes. Não gerar novas imagens.

O processo do GitHub Actions produz **8 segundos, 720×1280, 30 fps**, somente C12-P02 e C12-P03. A animação usa cinco PNGs RGBA isolados e cinco malhas reais, totalizando 512 triângulos. C12-P01 (movimento independente dos olhos de Kael) depende de camadas e underlays próprios e não será falsificado.

## Arquivos que precisam existir no repositório

Todos os caminhos a seguir são relativos à pasta deste episódio.

| Item | Caminho |
|---|---|
| Fonte original C12-P02 | assets/referencias/chat-aprovadas/confronto-trono-c12-p02.png |
| Fonte original C12-P03 | assets/referencias/chat-aprovadas/elara-close-trono.png |
| Fundo de P02 reconstruído | assets/planos/C12-P02/background-inpaint-technical.png |
| Capa de Kael | assets/planos/C12-P02/kael-cape-loose-fold.png |
| Fundo de P03 reconstruído | assets/planos/C12-P03/background-inpaint-technical.png |
| Mecha frontal | assets/planos/C12-P03/elara-left-face-hair-lock.png |
| Cabelo traseiro | assets/planos/C12-P03/elara-back-hair-fall.png |
| Brinco | assets/planos/C12-P03/elara-earring-pendant.png |
| Tecido da manga | assets/planos/C12-P03/elara-sleeve-lower-fabric.png |

Os três originais RGB (incluindo o close de Kael, necessário futuramente para C12-P01) foram preparados anteriormente no ZIP alchemy-ep01-cinema-3-originais.zip. A importação de originais existentes é feita pelo script scripts/enviar-referencias-cinema.ps1 e pelo workflow qa-alchemy-chat-cinematic-references.yml, sem geração de imagens.

O pacote técnico de sprites feito anteriormente no chat também precisa ser importado preservando exatamente os PNGs antigos. **O script não gera, redesenha, redimensiona ou reconstrói esses arquivos**: se o SHA-256 ou o recorte não corresponder, o render é bloqueado. As assinaturas SHA completas estão no módulo videoforge/c12_technical_preview.py e no contrato Remotion.

## Executar

1. Importar os PNGs antigos nos caminhos acima, sem modificar seus bytes.
2. Atualizar pedido-render-c12-tecnico.json (campo revision), ou executar manualmente o workflow render-alchemy-c12-three-mesh-technical.yml na branch main.
3. O script videoforge/c12_technical_preview.py verifica os SHA-256, a dimensão nativa 941×1672, os recortes RGBA e a malha 512-triângulos. Na ausência de arte, a execução termina com ASSETS_PENDING e deixa preflight.qa.json no artifact.
4. Com todas as fontes verificadas, o Remotion 4 renderiza via ThreeCanvas com --gl=swangle e gera MP4 H.264, cinco quadros de revisão, ffprobe.json e mp4.qa.json no artifact vf-alchemy-c12-threecanvas-draft-RUN_ID.

**QA antes de aprovação:** a máscara do brinco e da mecha frontal contém possível pele/fundo; verificar costuras, oclusão, underlays, textura nas bordas e continuidade. Nem um MP4 técnico pronto dá aprovação humana ou permissão de enviar ao YouTube. Permanecem falsos: human_visual_approved, video_oficial_do_programa e youtube_uploaded.
