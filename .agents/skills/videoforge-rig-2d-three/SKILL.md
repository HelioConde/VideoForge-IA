---
name: videoforge-rig-2d-three
description: Construir ou corrigir animacoes 2D articuladas no VideoForge com Three.js, React Three Fiber, Remotion e malhas, preservando o desenho original. Use para cabelo, capa, respiracao, olhar, maos, espada, props e QA de movimento.
---

# Skill — animador e engenheiro de rig 2D real

## Diagnóstico dirigido — 17/11/2026

**Precedência:** seguir [camadas geradas pelo proxy](../../../docs/CONTRATO-CAMADAS-GERADAS-PELO-PROXY.md). Peças finais exigem geração independente, proveniência e aprovação/recomposição antes do rig. Recortes/máscaras locais e os produtores históricos descritos abaixo são QA/legado, não fontes autorizadas de rig. Código mecânico com fixtures não equivale a rig da arte pendente.

- Peças cortadas, ROI de cor usada como textura ou fundo revelado: consultar [peças animáveis](../videoforge-animation-parts/SKILL.md).
- Mão/espada deslizando, pivôs ou malhas: consultar [contatos e deformação](references/contacts-and-deformation.md).
- Movimento mecanicamente válido mas artificial: consultar [atuação](../videoforge-character-acting/SKILL.md).
- Validar a sequência: consultar [QA temporal](../videoforge-qa-and-checkpoint/references/temporal-qa.md).

Carregar apenas a referência pertinente. Preservar versões do lockfile: skills globais mais novas podem conter APIs ainda indisponíveis no projeto.

## Bibliotecas e codigos prontos

- `three` e `@react-three/fiber` **ja instalados** para render de geometria, pivôs, texturas e malhas.
- `@remotion/three/ThreeCanvas` e `useCurrentFrame()` **ja instalados** para movimento deterministico sob Remotion.
- Reutilizar `motion-remotion/src/rig-three-scene.tsx` (`RigidSprite`, `DeformableSprite`, `CharacterParts`) e `motion-remotion/src/rig-three-math.ts` (`meshGridAtFrame`, head rotation, blink, pinned hair mesh).
- Para a espada da abertura C01-P02, reutilizar `motion-remotion/src/remake-sword-motion.ts` e `remake-sword-rig.tsx`; camada bainha fixa; lamina e mao com movimentos separados e pulso girando no proprio pivo.
- Referencia upstream do fabricante: [Three.js dentro de Remotion](https://github.com/remotion-dev/skills/tree/7e541aa4d7361dfaca0780a565a47307eb7bdfbb/skills/remotion-markup/3d.md). Manter versoes atuais da `package-lock.json` ate upgrade deliberado.

## Regras obrigatorias

1. Exigir imagem-mae correta, canal/shot, dimensoes, SHA e camadas RGBA independentes com underlays da mesma fonte.
2. Nao fazer qualquer `useFrame()`, `requestAnimationFrame`, `Math.random` ou fisica dependente do relogio. Usar quadros deterministas e parametricos.
3. Camadas articuladas tem proprio pivot: cabeca no pescoco; braço na junta; mao no pulso; espada acompanha a mão; bainha fica presa ao corpo. Deformacao de tecido por malha triangulada com vertices fixados nas costuras.
4. Nao animar PNG inteiro como substituto de rig; camera nao conta como movimento corporal.
5. Na ausencia de assets ou aprovacao, apenas criar codigo/testes e reportar `rig_aguardando_art`; nenhum render oficial.
6. Rodar testes do Remotion e comparar quadro neutro x imagem-mae; testar frames extremos, vedacoes, alpha, cabelos, pele e apoio dos objetos; arquivar resultados no canal.

## Biblioteca externa opcional

[Rigby2D](https://github.com/jaisurya-dev-art/rigby2d) possui malhas/IK e editor open source. **Nao integrar o runtime por padrao:** a regra principal do usuario preserva Three.js/Remotion e adicionar outro motor seria uma troca arquitetural nao aprovada. Pode-se estudar exportacao compativel futuramente, com revisao de licenca e QA.

### C01-P02: preview técnico real com pacote de sprites

Novo entrypoint `motion-remotion/src/remake-sword-preview-index.ts` usa `RemakeSwordTechnicalPreview` + ThreeCanvas; a imagem-mãe **nunca é movida** no player. O validador `videoforge/remake_sword_preview.py` só permite `sword-bundle.json` que corresponda ao artifact de origem, referência V2 aprovada e PNGs SHA-verificados de `scene-mother.png`, `underlay.png`, `sheath.png`, `blade.png`, `hand.png`. O QA recompõe a imagem neutra com FFmpeg (decodificação de PNG para QA) e Python stdlib (composição de pixels) e exige geometria real do pulso e deslocamento da lâmina; não basta uma máscara com alfa. `videoforge/remake_sword_preview_qa.py` confere movimento no MP4, 90 quadros, 30 fps e nenhum áudio fictício. A prévia tem watermark **ARTE NÃO APROVADA**, `technicalDraftOnly=true`, `humanVisualReview=false`, `youtubeUploaded=false`. Exemplo do contrato de fonte: `docs/C01-P02-PACOTE-ARTE-E-RIG.md`.

O workflow `.github/workflows/remake-sword-preview.yml` roda o **preflight gratuito** quando o código muda e aceita um artifact `vf-remake-c01-p02-sword-source-<run_id>` sob `workflow_dispatch` quando houver dados reais. O render real só executa após revisão e validação dos arquivos. Não usar esses testes para aprovar automaticamente estética, integridade de underlay sob deslocamento, ou publicação.



## C01-P02 — relatório de geometria por máscara real

Quando existir pacote de PNGs SAME-SHOT, rodar `python -m videoforge.remake_rig_geometry --package <source> --source-run-id <run> --write` somente no runner com FFmpeg e QA de fonte. Exigir `mask-geometry.qa.json` e reconferir com `--verify-report` antes do ThreeCanvas. BBox/centroide são medidas em pixels da imagem real; pivô de pulso e contato são **candidatos sujeitos à revisão humana**. Não inventar rig na ausência de PNG. Essas regras valem como preparação inicial da C01-P02 e devem ser generalizadas aos outros 38 visuais quando os produtores existirem.
