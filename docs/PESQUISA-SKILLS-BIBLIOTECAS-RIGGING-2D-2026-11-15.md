# Pesquisa de skills e bibliotecas GitHub — animação 2D por rig e malha

**Data do registro:** 15/11/2026 (America/Sao_Paulo). **Origem:** relatório de Pesquisa Aprofundada anexado pelo usuário nesta conversa como `Texto colado(1).txt`; SHA-256 do texto recebido: `950b66530b071e84e75b82ba5357c31629b8473ae908fc8ec5b1eb49a9256e84`. **Estado:** pesquisa/referência, NÃO código instalado, testado ou implementado. **Documento de aplicação obrigatória:** [manual de animação 2D](MANUAL-PRINCIPAL-ANIMACAO-2D.md), [checkpoint do episódio](../canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/ESTADO-ATUAL.md) e [regras corrigidas C01](../canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/REGRAS-ATUACAO-C01-P03-RESPIRACAO-2026-11-15.md).

> Este documento preserva **as informações técnicas e recomendações** do relatório fornecido, organizadas para o VideoForge-IA. Números de stars, últimos commits, versões, dependências e permissões de licenciamento registrados na pesquisa são **fotografia histórica e podem exigir confirmação**. A existência de uma biblioteca/skill no GitHub **não implica que ela esteja instalada, integrada, aprovada ou compatível**. Não copiar código com licença não comercial para o pipeline público/comercial sem revisão específica. A fonte textual integral permanece no arquivo original anexado na conversa.

## 1. Objetivo e restrições

- Projeto: [VideoForge-IA](https://github.com/HelioConde/VideoForge-IA), pipeline Python, Remotion/React, `@remotion/three`/ThreeCanvas e GitHub Actions. Episódio MMORPG `canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01`, C01 e C12.
- Meta: movimento por **partes RGBA, ossos, pivôs e malhas reais**, não pan, bob ou parallax do PNG inteiro.
- **Sem gerar novas imagens** para este episódio; reutilizar somente artes aprovadas e fontes SHA verificadas. Não fazer inpainting inventando anatomia oculta. Se faltar underlay real, limitar articulação e marcar pendência.
- **Não publicar no YouTube** antes da aprovação humana da estética/arte.
- C01: braço direito e mão apoiados na perna não fazem gesto independente; bota direita/tronco inferior não atuam; apenas respiração sutil do Kael; guardas e lanças rígidos; cabeça inteira do rei deve ser recuperada da fonte antes de liberar MP4 visualmente.
- C12: conservar cinco malhas/512 triângulos já registrados, mas não declarar o novo render concluído sem os dois ZIPs originais e nove PNGs SHA validados.

## 2. Os dois repositórios indicados

### [GenielabsOpenSource/spine-animation-ai](https://github.com/GenielabsOpenSource/spine-animation-ai)

- **Tipo:** skill de agente para preparar rig, estrutura de ossos e animações no formato Spine; não é um conversor direto de PNG em MP4 Remotion.
- **Na pesquisa:** Python 3.9+, OpenCV (SIFT/RANSAC), Pillow, NumPy e segmentação opcional por API Gemini. Scripts citados: `position_parts.py` (alinhamento das partes) e `build_spine_json.py` (skeleton/atlas); prévia HTML.
- **Aprendizado aproveitável:** correspondência geométrica de partes separadas com uma cena-mãe, detecção/alinhamento automático para revisar pivôs, geração de hierarquia e poses ociosas (*idle*).
- **Restrição importante:** a pesquisa identificou **PolyForm Noncommercial 1.0.0** no projeto e dependência do ecossistema/editor Spine. Tratar o algoritmo/fluxo como referência; **não importar código/redistribuir como se fosse MIT**. O editor e o runtime Spine têm termos próprios: conferir antes de qualquer integração comercial. Sprites sem máscara e sem região oculta não ficam automaticamente corretos só porque existe rig.

### [mromidev/claude-animated-shorts — SKILL.md](https://github.com/mromidev/claude-animated-shorts/blob/main/SKILL.md)

- **Tipo:** skill de planejamento/produção de curtas verticais com React, Remotion, `@remotion/three`, Three.js, Node, Python 3 e FFmpeg.
- **Na pesquisa:** exemplo narrativo completo com câmera, cenário, timeline, efeitos e áudio, com licença MIT indicada no repositório. O projeto advertia sobre recursos pesados da pasta `public/` e `REMOTION_TMP`.
- **Aprendizado aproveitável:** organizar direção, storyboard, tempos, composição de planos, renderização determinística por quadros, QA, documentação e templates de cenas.
- **Limite:** **não é ferramenta de auto-rig ou segmentação**, não substitui sprites/underlays de origem e não deve introduzir movimento de câmera para simular ossos.

## 3. Inventário comparativo da pesquisa

| Projeto | Área de uso | Stack / termos observados na pesquisa | Prioridade no VideoForge-IA e cautela |
|---|---|---|---|
| [spine-animation-ai](https://github.com/GenielabsOpenSource/spine-animation-ai) | Skill de auto-rig, alinhamento e hierarquia Spine | Python/OpenCV/Pillow/NumPy; PolyForm NC relatada | **Referência**, não copiar código não comercial nem supor render Remotion |
| [claude-animated-shorts](https://github.com/mromidev/claude-animated-shorts) | Storyboard, direção, render vertical | Remotion, Three, Python, FFmpeg; MIT relatada | **Alta** para métodos e organização de render; não resolve rig |
| [Rev2D](https://github.com/RevStudio/Rev2D) | Rig 2D JSON, mesh, IK, CLI/agentes | TypeScript/Node, MIT relatada | **Avaliar em experimento isolado**, conversão JSON para Three é trabalho adicional |
| [Rigby2D](https://github.com/jaisurya-dev-art/rigby2d) | Editor 2D, PSD, auto-rig, meshes, IK | JS/TS/Rust/Python; MIT/Apache relatadas | **Explorar**, checar maturidade, export e se consegue preservar pixels fonte |
| [Rive Runtime](https://github.com/rive-app/rive-runtime) | Motor/runtime de animação | C++/JS/WASM, editor Rive próprio | **Baixa para C01**: editor/formatos especiais; verificar licenças exatas |
| DragonBones | Ossos/malha e animação em runtime | JS/C++/C#; termos editor/runtime distintos | **Exploratório**, confirmar repositório oficial, editor, licença e adaptação |
| [PixiJS](https://github.com/pixijs/pixijs) | Sprites 2D, WebGL, filtros, malha | JavaScript, MIT relatada | **Alternativa**, só migrar se prova de benefício sobre Three |
| [Three.js](https://github.com/mrdoob/three.js) | Hierarquia, Bones, SkinnedMesh, deformação e câmera | JavaScript/WebGL, MIT relatada | **Prioridade máxima**: motor já adotado; corrigir joints, pivôs e máscaras |
| [IKPy](https://github.com/Phylliade/ikpy) | Cálculo de IK/pré-pose | Python, Apache-2.0 relatada | **Somente se preciso de IK real** em futuros planos; não melhora C01 de respiração parada |
| [Segment Anything](https://github.com/facebookresearch/segment-anything) | Máscaras guiadas de segmentação | Python/PyTorch, Apache-2.0 relatada | **Experimental/offline** para detectar máscara; não aceitar pixels inventados |
| [MediaPipe](https://github.com/google-ai-edge/mediapipe) | Detecção de pose/landmarks | Python/C++ e modelos de pose | **Baixa em anime estático**; métricas humanas não garantem poses 2D corretas |
| [OpenCV](https://github.com/opencv/opencv) | Correspondência, contorno, GrabCut, SIFT | Python/C++, licença permissiva relatada | **Alta** para alinhamento de partes, QA de bordas e segmentação local |
| [scikit-image](https://github.com/scikit-image/scikit-image) | Morfologia, métricas de diferença, regiões | Python, BSD relatada | **Alta** para máscaras, bordas, diffs e testes determinísticos |
| [FFmpeg](https://github.com/FFmpeg/FFmpeg) | Encoder/decoder e análise de quadros | CLI/C, licença depende dos componentes | **Já usado**; validar H.264 decodificado, não contar sucesso como estética |

**Checagem antes de adotar:** confirmar HEAD/atividade, versionamento, manutenção, licença de cada módulo (editor versus runtime), exigência de assinatura/uso comercial, compatibilidade com React/Remotion, uso de CPU/GPU no runner, custo, estabilidade do CI e preservação fiel de pixels aprovados. Os números de estrelas/commits da pesquisa não são critérios suficientes para instalar.

## 4. Três caminhos levantados

1. **Recomendado — evolução incremental do Three.js + Remotion atual.** Preservar cenas e workflow; adicionar *joint-lock*, pose neutra/hierarquia determinística, pequena respiração de malha, checagem dos sprites e máscaras; usar OpenCV/scikit-image no QA. Menor risco operacional e nenhum editor proprietário.
2. **Rig dedicado como protótipo separado.** Experimentar Rev2D ou Rigby2D e um export `rig.json` adaptado, comparando captura de quadros e pixels; não substituir pipeline principal antes de provar equivalência. Spine/DragonBones/Rive só sob compatibilidade e licenciamento verificados.
3. **Skills como instruções de agente, não como renderizadores mágicos.** Aproveitar os padrões de `SKILL.md` para especificar storyboard, animatic, rig-pivot, direção, validação e render. Comprovar cada etapa no Actions e não autorizar gerar novas artes para superar recortes ruins.

## 5. Plano técnico incremental para C01-P03

**Restrição corrigida pelo usuário após assistir V3:** menos movimentos é **melhor** para o drama da primeira tomada. A versão atual V3 passou um gate de movimento numérico, **mas foi rejeitada visualmente em braço/pé/lanças/rei**. A métrica de `16.000 pixels alterados` não deve impor gestos antinaturais: substituir por QA de amplitude, área de atuação esperada, estabilidade dos membros travados, continuidade temporal e qualidade visível.

### Etapa A — congelar pose e objetos

- Carregar a configuração atual `direcao-rig-remotion.json` e `direcao-bindings-c01-draft.json`; criar novo pedido C01 V4 em branch própria.
- Travar **juntas locais e posições globais** do braço direito, antebraço, pulso, mão, perna/bota direita. Como o braço é filho do osso do ombro, *lock local sozinho não basta*: impedir que o pai móvel desloque a mão ancorada na perna; usar world-space hold/IK com 2 pontos de contato ou separar o braço de transformações respiratórias.
- Não animar lanças, guardas, rei, trono e cenário. **Não aceitar a cabeça do rei cortada na pose neutra**: consertar recorte/composição usando a arte aprovada e guardar evidência de pixels/hashes, antes do próximo MP4.
- Remover do primeiro plano as `tracks` de mão/pé/antebraço que geram gesto independente. Manter fidelidade dos pixels e z-order.

### Etapa B — respiração de Kael apenas

- Recomendações de referência a calibrar nos pixels nativos: oscilação de tórax/ombros ≈ ±1–2 px de fonte, sem mobilizar o ponto de contato braço/perna; cabeça ≤0,5° de inclinação local, sem desencaixar gola; cabelo/jaqueta com malha secundária mínima, sem efeito de vento.
- Sinal suave, frame-determinístico e limitado, ex. `breath = sin(2π*frame/(30*2.5))`. Aplicar somente nos vértices do tronco/ombros e atenuar nas articulações fixas. Nenhum pan/zoom como substituto.
- Criar preset `first_scene_subtle_breathing` para cenas estáticas com movimentos causais e pequenos, sem adotar como regra de atuação de todas as cenas futuras.

### Etapa C — máscaras, holdouts e QA

- Revisar juntas com máscara `alpha`, recortes `onlyCoveredBy`, origem SHA e overlap. Se não houver pixels originais de pescoço/manga, não fabricar conteúdo: reduzir amplitude.
- QA do frame 0 contra a imagem-mãe aprovada; **reprovar rei com cabeça cortada, lanças deformadas e qualquer membro com gap/silhueta quebrada**.
- Testes automatizados: quadros iniciais/finais, sombra/alpha e fundo vazado, máscaras e bounding boxes de Kael/rei/guardas, continuidade de quadros H.264, movimento apenas na ROI de respiração; mão direita e bota ancoradas com deslocamento máximo próximo de zero. Mudanças fora de Kael: idealmente nenhuma (ou tolerância de codec explicitamente documentada).
- Prévia MP4 técnica 3 segundos só após testes. **Aprovação visual humana é necessária mesmo se todos os testes passarem**.

**Pseudocódigo de direção (conceitual, não implementação atual):**
```text
rig = loadApprovedC01()
lockWorld(Kael.rightHand, contact=Kael.rightKnee)
lockWorld(Kael.rightForearm, contact=Kael.rightKnee)
lockWorld(Kael.rightBoot, contact=ground)
freeze([guards, spears, king, throne, background])
for frame in 0..89:
  a = sin(2*pi*frame/(30*2.5))
  breatheMesh(Kael.chest, amplitudeSourcePx=1.5*a, anchors=[shoulderRoot, waist])
  rotate(Kael.head, maxAbsDeg=0.5)
  preserveContactPoints()
  assertAllSourcePixelMasks()
  render(frame)
verify(neutralRecomposition, kingHeadIntact, staticProps, anchoredHandAndFoot, seamNoGap)
```

## 6. C12 — pendência independente

- Arquivos antigos identificados: `uploads/alchemy-ep01-cinema-3-originais.zip` (3 PNG RGB) e `uploads/alchemy-c12-rig-camadas-tecnicas-v2.zip` (7 técnicos: 2 fundos + 5 sprites RGBA).
- O coordenador de importação só prossegue após os **nove PNGs de origem exigidos** estarem presentes e com SHA-256 correto; a falta dos ZIPs **não deve provocar regeneração de arte**. O novo MP4 C12 de 8 s não pode ser presumido.
- Reutilizar a malha/rig existente, validar neutralidade, recortes/oclusões, áudio, versão final e aprovação humana.

## 7. Checklist para o próximo MP4

- [ ] Cabeça do rei Aldric **inteira** no frame inicial, sem duplicação/corte, comparada com fonte aprovada
- [ ] Lanças rígidas e guardas fixos, sem pontas duplicadas, deformação ou partes flutuantes
- [ ] Kael ajoelhado com braço/mão direitos **apoiados continuamente na perna**
- [ ] Pé/bota direitos sem movimento independente, cortes ou transparência
- [ ] Só respiração pequena e natural do tórax/ombros de Kael; cabeça e cabelo discretos
- [ ] Pose neutra recompõe os pixels da fonte nos elementos estáticos
- [ ] QA por ROI do H.264 e de máscaras/alpha/z-order, sem usar parallax para mascarar falhas
- [ ] Render técnico validado por Actions, revisão humana antes de marcar aprovado
- [ ] Sem novas imagens, sem custos externos inesperados, sem YouTube, sem substituir o código funcional

## Fontes e rastreabilidade

- **Fonte primária deste registro:** relatório recebido em 15/11/2026, `Texto colado(1).txt`, SHA-256 `950b66530b071e84e75b82ba5357c31629b8473ae908fc8ec5b1eb49a9256e84`; suas conclusões foram condensadas sem tratar código ainda não integrado como pronto.
- Projetos externos citados são links para avaliação técnica; confirmar licenças e compatibilidade diretamente na versão escolhida ANTES de copiar código.
- Se um agente precisar da íntegra literal do relatório original, solicitá-la a partir do arquivo anexado; este documento é um registro operacional fiel das **informações úteis**, não uma transcrição palavra por palavra.
