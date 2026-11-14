# Animação por direção e peças articuladas

Data: 2026-11-14. Implementação opt-in para diagnóstico, conforme o
[manual principal](MANUAL-PRINCIPAL-ANIMACAO-2D.md). O motor aprovado
`rig-three/v1` permanece separado e suas exigências não foram alteradas.

## Problema e comportamento implementado

O dorama de Alchemy Lab contém 14 cenas, 37 planos e 107 trilhas em
`direcao-rig-remotion.json`. O render anterior não consumia essas trilhas.
Agora `videoforge.directed_rig` resolve alvos da direção para nós independentes
e prepara a composição `VideoForgeDirectedRigScene` em ThreeCanvas.

Cada nó tem um pivô no canvas original, pai opcional e ordem de composição.
Assim, uma mão acompanha o antebraço e a cabeça acompanha os ombros sem
deslocar as pernas. Rotação, translação e escala seguem keyframes absolutos,
com interpolação limitada e easing declarado. Cabelo e roupa usam
BufferGeometry com raízes fixas; a câmera perspectiva inclui o fundo.
Tudo depende do frame, sem relógio ou física acumulada.

O manifesto `videoforge/direction-bindings/v1` identifica canal, episódio,
cena-mãe, fundo e peças por SHA-256. Os arquivos são relativos à pasta do
episódio. `bbox` significa **x, y, largura, altura** em pixels da mãe;
`pivot` usa as mesmas coordenadas. Os arquivos de entrada são PNGs full-canvas;
o empacotador recorta o bbox preservando os pixels. Nós sem arquivo são grupos.
O `target` de cada trilha deve coincidir exatamente com um ID de nó.

Arquivo ausente, SHA divergente, caminho externo, ciclo na hierarquia,
trilha sem alvo, timeline inválida e metadados incompatíveis interrompem a
preparação. Ausências de outros planos aparecem no relatório de cobertura.
Não existe aprovação automática: esta entrada só gera rascunhos marcados,
com `humanVisualReview=false` e `publishable=false`.

## Executar o programa

O workflow [directed-rig-preview.yml](../.github/workflows/directed-rig-preview.yml)
reutiliza o runner `rig-three-remotion4-v1`, sem instalar ferramentas a cada
render. Em PR, valida o exemplo do Alchemy Lab; depois de integrado à main,
aceita canal, episódio, bindings e plano em `workflow_dispatch`.

Preparação local, sem IA (PowerShell; requer Python e FFmpeg):

```powershell
$episode = 'canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01'
$target = 'output/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/directed/C01-P03'
python -m videoforge.directed_rig inspect --direction "$episode/direcao-rig-remotion.json" --bindings "$episode/direcao-bindings-c01-draft.json" --output "$target/coverage.json"
python -m videoforge.directed_rig prepare --direction "$episode/direcao-rig-remotion.json" --bindings "$episode/direcao-bindings-c01-draft.json" --shot C01-P03 --output-dir $target --public-dir motion-remotion/public
```

A preparação recusa sobrescrever props ou peças empacotadas. Use workspace
limpo para repetir; os outputs ficam fora do Git. O render rastreável é
feito no Actions, usando `src/directed-rig-index.ts`, composição
`VideoForgeDirectedRigScene`, H264/yuv420p, `--gl=swangle --concurrency=1`.

## Artefatos e limites

O run entrega MP4, stills, props, cobertura, hashes das entradas, recomposição
neutra, diff amplificado e contact sheet. A contact sheet mostra, da esquerda
para a direita: mãe original, composição candidata, diferença absoluta ×3.
QA mede movimento fora da UI tanto nos PNGs quanto em frames decodificados do
MP4, exige repetição idêntica de um still e verifica formato/duração.

Isso verifica a execução técnica. Não comprova anatomia, pivôs medidos,
continuidade dramática ou qualidade visual. O exemplo C01-P03 usa pivôs
provisórios e peças ainda sem underlays: seu objetivo é revelar falhas.
O frame zero deve ser inspecionado antes dos frames em movimento.

O programa prepara um plano por execução; a composição aceita planos
contíguos, mas a montagem integral do episódio, voz, efeitos sonoros,
legendas e aprovação de arte continuam em etapas separadas. O dorama
completo ainda não é um vídeo oficial pronto.

## Testes

```powershell
python -m unittest tests.test_directed_rig tests.test_directed_rig_qa tests.test_rig_three_contract -v
cd motion-remotion
npm run typecheck
node --test tests/directed-rig.test.cjs tests/rig-three-math.test.cjs
```

Os testes cobrem coordenadas pai/filho, cortes, interpolação, ordem aleatória
de frames, raízes de malha, recortes exatos, SHA/caminhos, aprovação falsa,
UI excluída da medição e rejeição de MP4 estático acompanhado de stills móveis.
