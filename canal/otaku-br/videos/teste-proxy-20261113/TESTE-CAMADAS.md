# Teste de separacao de camadas — otaku-br / teste-proxy-20261113

Data: **13/11/2026**. Registro de experimento de IA **sem video publicado**. Este arquivo documenta somente provas efetivamente vistas nos logs, no manifesto e nos PNGs dos artifacts. Nao significa que a animacao ja foi implementada.

## Origem da cena

- [Imagem gerada pelo nosso Codex Proxy](https://github.com/HelioConde/VideoForge-IA/actions/runs/43433023378) — `cena-01.png`, 1024 x 1536, artifact `imagem-otaku-br-teste-proxy-20261113-43433023378`.
- Cenario original: aventureiro de capa vermelha em telhado de cidade fantastica ao por do sol.
- Todas as edicoes utilizaram o **mesmo PNG** como referencia `images[0].image_url` via `POST /v1/images/edits`. A imagem-base NAO foi regenerada.

## Execucoes e evidencias

| Teste | Run aprovado | Artefato | Resultado |
|---|---|---|---|
| Teste 1: fundo e personagem | [43437394037](https://github.com/HelioConde/VideoForge-IA/actions/runs/43437394037) | `camadas-basic-otaku-br-teste-proxy-20261113-cena-01-43437394037` | `background.png` RGB e `character-main.png` RGBA |
| Teste 2: foreground e capa | [43437992955](https://github.com/HelioConde/VideoForge-IA/actions/runs/43437992955) | `camadas-advanced-otaku-br-teste-proxy-20261113-cena-01-43437992955` | `foreground-roof.png` RGBA e `cape.png` RGBA |

**Todos os quatro PNGs têm 1024 x 1536 pixels e verificação técnica aprovada.** Hashes SHA-256, z-index e campos de QA encontram-se no `manifest.json` do artifact da etapa 2.

Fraçao de pixels com alfa exatamente zero: personagem **61,85%**, telhado frontal **74,51%**, capa **87,91%**. A checagem rejeita PNG opaco fingindo recorte. Nao mede automaticamente a qualidade das bordas, alinhamento visual ou originalidade.

## Verificacao visual inicial

- O background gerado remove visualmente o aventureiro e preenche o cenario. Ainda precisa de QA detalhado para inpainting e fidelidade exata.
- O personagem aparece isolado, com pose e figurino reconheciveis. Ha variacoes pontuais possiveis que devem ser avaliadas por comparacao lado a lado.
- O telhado frontal saiu como elemento independente, com fundo transparente.
- A capa saiu como elemento separado, mas a **capa continua dentro do PNG completo do personagem**. Para animar a capa sem duplicacao, criar uma versao do corpo sem a capa (ou outra estrategia de composicao/mascara) antes da montagem.
- **Pixel alignment e consistencia ainda nao foram aprovados por humano.** Esses testes nao implementaram rigs, bonecos recortados, animacao ou MP4 real.

## Pendencias e proximos testes

1. Avaliar sobreposicao com alfa em resolucao integral; conferir se contornos, telhado, personagem e capa coincidem.
2. Gerar o corpo sem capa e avaliar substituicao da capa isolada, evitando "capa dupla".
3. Usar o [Teste 2 manual](../../../../.github/workflows/scene-layers-advanced.yml) com `source_run_id=43437394037` e componentes individuais para cabelo, espada, bandeira ou cachoeira **apenas se existirem na cena**.
4. Implementar motor de composicao e movimento em fase posterior, com teste visual frame a frame.
5. Artifacts sao temporarios (retencao de 7 dias para camadas). **Nao versionar os PNGs nem os tokens.**

Guia de implementacao transversal: [docs/TESTE-CAMADAS-CENA.md](../../../../docs/TESTE-CAMADAS-CENA.md). Toda nova sessao de teste de outro canal deve receber seu proprio registro em `canal/<id>/videos/<video-id>/`.


## 13/11/2026 — Teste 3 de animacao por camadas (REAL)

- [Workflow de renderizacao animada aprovado — run 43453893646](https://github.com/HelioConde/VideoForge-IA/actions/runs/43453893646).
- Artifact: `animacao-otaku-br-teste-proxy-20261113-cena-01-43453893646`. Contem `teste-parallax.mp4`, `teste-parallax.qa.json` e `movimentos.json`.
- Entrada: artifact do Teste 2, run `43437992955`, importando e validando os hashes das imagens ja geradas. Nenhuma nova inferencia de IA nem acesso a tokens Codex foi necessario.
- Resultado confirmado por `ffprobe`/QA: **8,0 segundos**, **1080×1920**, **24 fps**, **H.264 + AAC silencioso**, SHA-256 do MP4 `90784b39495c213cabeb2d6cc8ee591a96b0ae12ba7b70dab3cfe996951e129a`.
- Verificacao tecnica de movimento: quadros decodificados em instantes diferentes tiveram checksums diferentes; `motion_detected=true`. O resultado e um video tecnico de revisao, **nao um Short final**.
- Tracks animados: `background` (pan lento/overscan), `character-main` (movimento sutil de respiracao) e `foreground-roof` (parallax na frente da camera).
- `cape_overlay_enabled=false`: a capa ainda existe dentro do PNG do personagem. A versao isolada nao pode ser sobreposta com movimento antes de remover a capa original do corpo e conferir encaixe.
- Audio presente e **silencio proposital**: `narration_present=false`. Nao houve lip sync, rig de membros, articulacao de cabelo/espada ou upload no YouTube.
- `visual_approval=pending` e `pixel_alignment_verified=false`. Nao concluir qualidade da composicao ou adequacao editorial somente pelo MP4 tecnico; comparar quadros e revisar bordas/cobertura/duplicacao.

**Proxima fase:** produzir `character-body-no-cape.png` (reconstruindo partes encobertas), definir pivô/mascara da capa e testar movimento isolado da capa com QA de composicao; depois olhos, cabelo, espada, bandeiras e outros itens conforme a cena.

Codigo e guia geral: [docs/ANIMACAO-CAMADAS.md](../../../../docs/ANIMACAO-CAMADAS.md). O renderizador completo de `modelos/camadas-animadas` permanece desabilitado.


## 13/11/2026 — Remotion original reutilizado e MP4 gerado

- [Execução aprovada do workflow Remotion — run 43458182424](https://github.com/HelioConde/VideoForge-IA/actions/runs/43458182424)
- Artifact: `remotion-otaku-br-teste-proxy-20261113-cena-01-43458182424` (run do Teste 2 que forneceu as camadas: `43437992955`).
- Entrada: os mesmos `background.png`, `character-main.png`, `foreground-roof.png` e metadados SHA-256. Não houve nova inferência de imagem.
- **Motor de animação desta versão: Remotion** (`motion-remotion/src/scene-layer-preview.tsx`, composição `VideoForgeLayerScene`), com módulos importados do AutoEditorVideo e do VideoForge anterior. A versão FFmpeg continua arquivada como teste separado.
- MP4 validado: **8,000 s, 1080 x 1920, 30 FPS, H.264 e AAC silencioso**. SHA-256 `413b7fcfa0d1eb930816e3c319943ff999abcf34a60c3ee5e1a30759364dcab5`.
- Movimentos por quadro: câmera cinematográfica `cinematic-motion.ts`, personagem `character-idle.ts`, e telhado em primeiro plano `videoforge-motion.ts`. QA detectou diferença entre quadros decodificados; não é rigging de personagem.
- O container `ghcr.io/helioconde/videoforge-remotion-runner:legacy-ec85db5-v1` forneceu Node/Remotion/Chrome pré-instalados, sem executar npm ci ou download de Chrome por render.
- **Limites:** `cape_overlay_enabled=false` (sem duplicação de capa), `body_part_rigging_implemented=false`, `visual_review=pending`, `pixel_alignment_verified=false`, sem narração e sem publicação YouTube. Os movimentos são propositadamente sutis e as bordas de todas as camadas ainda exigem revisão em resolução integral.
- O artifact e o MP4 não são versionados no Git; permanecem disponíveis no Actions até o prazo de retenção.

Documentação do novo motor e parâmetros: [docs/REMOTION-ANIMACAO.md](../../../../docs/REMOTION-ANIMACAO.md).

## 13/11/2026 — Rig por malha: candidatos REAIS, frames e MP4 de revisão

**Não há aprovação humana nem publicação.** A pesquisa de preparação por cutout+reconstrução parcial foi aplicada ao material real do Teste 2, sem consumir chamadas de IA.

- [Run da preparação dos PNGs RGBA — 43498887979](https://github.com/HelioConde/VideoForge-IA/actions/runs/43498887979): artifact `rig-candidate-otaku-br-teste-proxy-20261113-cena-01-43498887979`. O código valida os hashes do Teste 2 e extrai **seis sprites candidatos** (corpo, cabeça, dois estados de olho e capa dividida em traseira e frontal), máscaras, contact-sheet, plano de pivô e provenance.
- O desenho real possui **um olho principal e um segundo olho parcialmente visível sob a franja**, não apenas um olho. O `rig-plan.json` contém polígonos aproximados visualmente, ainda não aprovados.
- O `candidate.qa.json` registrou **225.842 pixels apagados do corpo que requerem reconstrução**, cerca de **37,63% da área visível do personagem**. O preenchimento provisório do olho fechado e a junção das capas ainda precisam de intervenção artística. `human_visual_approval=false`, `rig_ready_for_remotion=false`.
- [Run de prévia articulada com clip SVG corrigido — 43500330004](https://github.com/HelioConde/VideoForge-IA/actions/runs/43500330004): artifact `rig-draft-preview-otaku-br-teste-proxy-20261113-cena-01-43500330004`, contendo MP4 e PNGs dos quadros 0, 40, 60, 132 e 239 com marca d'água **RASCUNHO — SEM RECONSTRUCAO/QA VISUAL**.
- QA desse MP4: **8 segundos, 1080×1920, 30 FPS, H.264, AAC silencioso**, SHA-256 `51eeef037af60506e8d947f7c6483bc63a4bf253c97cfaae8510d611d5544492`. `publishable=false`, `youtube_uploaded=false`, `asset_human_approval=false`, `body_inpainting_completed=false`.
- Primeira versão do warp tinha **fendas de antialias** entre triângulos; o clip SVG foi expandido em 2 px para sobrepor as bordas. Inspeção visual do quadro 60 da versão corrigida mostrou melhora. Os olhos fechados continuam esteticamente provisórios.
- O workflow `rig-draft-preview.yml` é **manual**, para evitar re-renderizar 8 segundos a cada mudança no código; a versão renderizável oficial `remotion-animate-layers.yml` permanece bloqueada para sprites candidatos.

Próxima ação artística: ajustar máscaras do cabelo e olhos, fazer inpainting localizado de pescoço/ombros/costas, validar os seis PNGs contra a composição original em escala 100% e só então considerar `human_review=true` e um primeiro vídeo articulado **não rascunho**.

Guia operacional: [docs/PREPARAR-RIG-CANDIDATO.md](../../../../docs/PREPARAR-RIG-CANDIDATO.md). Resultados de vídeo e imagens continuam exclusivamente nos artifacts e em `output/otaku-br/videos/teste-proxy-20261113/`, sem versionar MP4/PNG no Git.
