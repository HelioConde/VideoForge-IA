# C01-P02 — contrato de produção da espada no GitHub

## Proteção de retrabalho por run e origem (15/11/2026)

Antes de consumir provedor, `remake_sword_source.preflight/produce` procura na pasta permanente `assets/geracoes` uma parte técnica válida da **mesma** mãe, no run de origem correspondente. Um runner novo não deve regenerar e cobrar por algo arquivado; erro `REMAKE_SWORD_COMPONENT_ALREADY_ARCHIVED_SAME_MOTHER` é bloqueio positivo de duplicação. Saídas rejeitadas por PNG/alfa não contam como sucesso. A etapa de revisão artística mantém poder de reprovar imagens e requer planejamento explícito do retrabalho.

O packer rejeita `scene`, `shot_id`, `part_id`, produtor e `source_archive_run_id` que não correspondam à mãe `C01-P02`, mesmo que outros hashes sejam válidos. Os testes dessa mudança **não** produzem arte. Política de gasto e upload continua idêntica; CI precisa comprovar a implementação antes de marcá-la validada.

## Auditoria de geometria de rig por pixels da fonte (15/11/2026)

O módulo `videoforge/remake_rig_geometry.py` **não desenha imagem nem simula movimento**. Ele consome o `sword-bundle.json` já verificado pelo `remake_sword_preview.validate_package`, decodifica os PNGs reais de **bainha/lâmina/mão** com FFmpeg apenas para QA e mede **bbox XYXY, centroide e pixels com alfa maior que 127**. O underlay tem que ser RGB8 integralmente opaco; a recomposição neutra com a imagem-mãe da mesma tomada tem que continuar com MAE ≤ 0,5. O relatório `mask-geometry.qa.json` guarda SHA da mãe e âncora, ID do run, SHA de cada camada, fingerprint das quatro instruções do V2, pivô de punho **candidato**, poses matemáticas nos frames 0/7/72/89 e avisos explícitos `human_anatomy_contact_review_required=true` e `rig_approved_for_official_render=false`.

O `remake-sword-pack.yml` só publica fonte se a auditoria concluir, e inclui o relatório no artifact de 90 dias. O `remake-sword-preview.yml` baixa o artifact e executa `--verify-report` **antes** do render ThreeCanvas; recalcula tudo a partir dos PNGs para rejeitar relatório falsificado ou origem alterada. Testes positivos usam apenas PNGs sintéticos temporários isolados no runner, nunca salvos no canal. O scanner gratuito não fabrica `mask-geometry.qa.json` quando faltam imagens.

**Limitação real:** as posições de pivô são inferências baseadas em máscara e seguem sem aprovação anatômica. Não há fonte de C01-P02 no repositório, portanto não foi produzida medição ou MP4 dessa tomada. O trabalho de geometria das demais tomadas começa após a respectiva mãe e camadas reais existirem.

## Gerador da C01-P02 — mão, lâmina, bainha e underlay por tomada (15/11/2026)

**Código novo:** `videoforge/remake_sword_source.py` usa `proxy_images.call_proxy`, `scene_layers.png_info`, `image_generation_policy.assert_image_generation_allowed` e o arquivo permanente `production-scene-request/<run-id>/cena-01-c01-p02.png`. Nunca usar `cena-01.png` genérica (o produtor legado se baseava no quadro amplo C01-P04). A âncora de personagem V2 já precisa estar aprovada por SHA, e a imagem-mãe precisa ter proveniência `shot_id=C01-P02` no arquivo principal. Cada camada recebe **exatamente uma** edição da mesma imagem-mãe, com prompt específico para o carrasco e para a arma, sem ângulos aleatórios.

**Workflow dedicado:** `.github/workflows/remake-sword-component.yml` tem dois modos. `push` roda **somente testes gratuitos/mockados**. `workflow_dispatch` exige `part_id` (`underlay`, `sheath`, `blade`, `hand`) e `source_run_id` da imagem-mãe arquivada. A primeira etapa interrompe antes de usar segredos/proxy se faltar custo aprovado, âncora ou mãe genuína. A política continua com `paid_provider_calls_approved=false`, `max_chargeable_calls_per_run=0` no estado atual: **não autoriza geração**; nenhuma chamada paga é disparada por `push` ou pela automação de pacote.

**Output e acervo:** em produção futura, cada run gera só uma imagem. `underlay` deve ser PNG RGB opaco, sem silhuetas fantasmas/duplicações; `sheath/blade/hand` devem ser PNG RGBA8 com alfa real. O código preserva PNG produzido mesmo quando QA rejeita, com `<part>.qa.json` `technical_status=rejected_png_or_alpha_invalid`, para revisão. Apenas status `candidate_opaque_verified` / `candidate_rgba_verified` entra no empacotador, que ainda exige recomposição neutra MAE ≤ 0,5 e validações completas. O workflow arquiva a saída no canal via `persistir-imagens-gh.sh`: produtor `production-sword-underlay-request` para underlay e `production-rgba-request` para as outras peças, IDs de run e SHA imutáveis, além de artifact temporário. `human_visual_approval`, `rig_applied`, `official_video`, `youtube_uploaded` permanecem falsos.

**Não houve geração nesta implementação.** Gasto, anatomia, textura, máscara, underlay e contato com lâmina precisarão de revisão real quando houver fonte autorizada. Só então `remake-sword-pack.yml` poderá juntar peças e disparar automaticamente a prévia técnica em ThreeCanvas.

## Empacotamento automático por arquivos permanentes (15/11/2026)

**Novo:** `videoforge/remake_sword_pack.py` e `.github/workflows/remake-sword-pack.yml` pesquisam os PNGs **originais** no diretório permanente `assets/geracoes/<produtor>/<run-id>/`, verificando `manifesto-geracoes.json`, SHA, canal, vídeo, tomada e origem. O `scan` não chama IA; o empacotador só é acionado quando todos os arquivos verdadeiros existirem. O `workflow_run` de `remake-sword-preview.yml` confere a presença do artifact no GitHub antes de despachar o render ThreeCanvas. Se não houver artifact, nenhum render ocorre.

**Fonte esperada:**
- `production-scene-request/<run-id>/cena-01-c01-p02.png` com relatório `cena-01-c01-p02.production.json`; o campo técnico de cena do `roteiro.json` é **`c01`**, e a tomada é `C01-P02`. A prancha V2 deve ter sido aprovada e vinculada por SHA.
- `production-rgba-request/<run-id>/{sheath,blade,hand}.png` com `<part>.qa.json`, cada uma indicando `scene_mother_sha256` idêntico à mãe C01-P02.
- `production-sword-underlay-request/<run-id>/underlay.png`, opaco, com `underlay.qa.json`, schema `videoforge/remake-underlay-candidate/v1`, tomada C01-P02 e mesmo SHA da mãe. **O produtor específico de underlay foi programado em `remake_sword_source.py`, mas ainda não produziu PNG real por falta de autorização de custo/âncora.** O produtor atual de sprites RGBA ainda precisa receber a tomada e mãe C01-P02, não os arquivos genéricos C01-P04.

O pacote aprovado tecnicamente é `vf-remake-c01-p02-sword-source-<run-id>`, com os cinco PNGs, `scene-mother.production.json`, `sword-bundle.json` e `package.qa.json`. O `source_run_id` do bundle indica o job de empacotamento; `source_archives` registra os jobs anteriores individualmente. **Aprovado tecnicamente NÃO é aprovado visualmente.**

O movimento provisório usa `wristPivot` e distância/ângulo estimados da silhueta real RGBA (sem parâmetros fictícios de arquivos inexistentes). Ficam marcados `draft_motion_heuristic_only=true` e `human_motion_review_required=true`. Se não houver espaço para movimento plausível, o teste bloqueia. A documentação/histórico devem preservar toda negativa, sem alegar vídeo completo. A guarda `REMAKE_PACK_SAME_SOURCE_ALREADY_RENDERED_TECHNICALLY` impede reconstruir infinitamente o mesmo pacote depois de QA.

**Estado:** sem `character-bible` V2 aprovada ou as 4 camadas reais, o `scan` apenas aponta o bloqueio. Não houve imagem paga, artifact de fonte ou MP4 da C01-P02 neste trabalho.

**Data:** 15/11/2026. **Regra:** `AGENTS.md` → `docs/MANUAL-PRINCIPAL-ANIMACAO-2D.md` → `remake-ep01-planos.json` → esse contrato. Nunca substituir a imagem-mãe pelo pôster V1 ou inventar PNGs. Prévia técnica ≠ vídeo oficial.

## Origem, tomada e arte

- Canal: `alchemy-lab`; vídeo: `mmorpg-conquiste-a-princesa-ep01`; cena/tomada `C01-P02`.
- O trecho ocupa **frames globais 60–149** (3 segundos, 90 frames a 30 FPS).
- Espada pertence ao **carrasco**, mão enluvada. Macro/insert de mão, lâmina e bainha, sem rostos. Direção `remake-ep01-planos.json`.
- Fonte obrigatória: **uma imagem-mãe 1024×1536 da própria C01-P02**, derivada da âncora V2 de personagens aprovada, com `scene-mother.production.json` do produtor `videoforge/production-scene/v1` (campos `shot_id`, `number=1`, `reference_sha256`, `sha256`). Referência antiga de outro enquadramento é recusada.
- Camadas independentes de mesmo canvas: **`underlay.png`** (fundo reconstruído e opaco), **`sheath.png`**, **`blade.png`**, **`hand.png`** (RGBA com transparência verdadeira). A recomposição em pose neutra precisa reproduzir o RGB da imagem-mãe, com MAE automática máxima 0,5; revisão de costuras, máscara e anatomia escondida continua humana.
- Pivô `wristPivot=[x,y]` **medido na mão da arte**; `draw` contém `beginFrame`, `finishFrame`, `travelPx`, `axisDeg`, `handFollow`, `handRotationDeg`. Ajustar pelas proporções reais; valores de código de teste não são medidas da arte.

## Artifact consolidado de origem

Para usar o fluxo quando as imagens reais estiverem disponíveis, um empacotador/agente deve reunir os arquivos sob um único artifact do GitHub Actions com nome `vf-remake-c01-p02-sword-source-<run_id>`. Esse mesmo `run_id` entra no `sword-bundle.json` e na entrada manual do workflow. **O empacotador e o produtor de sprites/underlay por tomada estão programados; a geração de imagens reais segue bloqueada até aprovação de custo e fonte V2.**

```text
sword-bundle.json
scene-mother.png
scene-mother.production.json
underlay.png
sheath.png
blade.png
hand.png
```

Exemplo de **estrutura**, sem valores falsos de SHA ou de aprovação (preencher a partir de arquivos reais auditados):

```json
{
  "schema": "videoforge/remake-c01-p02-layer-bundle/v1",
  "channel": "alchemy-lab",
  "video_id": "mmorpg-conquiste-a-princesa-ep01",
  "shot_id": "C01-P02",
  "source_run_id": 0,
  "source_artifact": "vf-remake-c01-p02-sword-source-<run_id>",
  "anchor_sha256": "<sha256_real_da_ancora_v2_aprovada>",
  "sha256": {
    "scene-mother": "<sha256_real>",
    "underlay": "<sha256_real>",
    "sheath": "<sha256_real>",
    "blade": "<sha256_real>",
    "hand": "<sha256_real>"
  },
  "wristPivot": [0, 0],
  "draw": {
    "beginFrame": 7,
    "finishFrame": 72,
    "travelPx": 0,
    "axisDeg": 0,
    "handFollow": 0,
    "handRotationDeg": 0
  },
  "human_visual_approved": false,
  "official_video_approved": false,
  "youtube_uploaded": false
}
```

Os zeros e marcadores acima **não são parâmetros executáveis**; o validador rejeita arte inexistente, SHA fictício, pivô fora da mão e curso inválido.

## GitHub Actions e revisão

O workflow `.github/workflows/remake-sword-preview.yml` executa gratuitamente, em pushes de código, o `preflight` e testes de bloqueio. Com artifact fonte completo e verdadeiro, o mesmo workflow pode ser despachado com o número do run. O contêiner GHCR é responsável pelo Python/FFmpeg para decodificação e Python stdlib para recomposição, Remotion/ThreeCanvas com SWANGLE e FFprobe/FFmpeg de QA; o host Git é responsável por gravar apenas SHA, relatório e histórico.

O render usa entrada `motion-remotion/src/remake-sword-preview-index.ts`, composição `VideoForgeC01P02SwordTechnical`. O MP4 de 3 segundos terá watermark explícita de **prévia técnica não aprovada** e irá para artifact, não para o Git do canal. Se o QA passar, `videoforge/remake_sword_checkpoint.py` registra `QA-C01-P02-REMAKE-V2.json` e os hashes no estado; sem aprovação visual, nunca integrar como vídeo oficial ou publicar no YouTube.

**Limite real atual:** a âncora visual V2 ainda não está arquivada/aprovada, e as quatro camadas específicas não existem. Portanto o preflight deve informar o bloqueio; nenhum MP4 C01-P02 pode ser afirmado até evidência de workflow e bytes de mídia.

## Verificações automatizadas registradas (15/11/2026)

O código de fonte e preview passou no [run 43711300246](https://github.com/HelioConde/VideoForge-IA/actions/runs/43711300246) com recomposição numérica de PNGs de teste, SHA e rejeição de máscaras adulteradas. O [run 43711476006](https://github.com/HelioConde/VideoForge-IA/actions/runs/43711476006) comprovou que o Remotion/ThreeCanvas realmente renderiza dois frames diferentes (7 e 71) utilizando quatro camadas **sintéticas de CI**. Isso não gera MP4 do dorama, nem aprovação humana. Próximo passo: arte canônica V2 aprovada e pacote real por tomada.

## Evidências do empacotador automático — 15/11/2026

[Run 43745321463](https://github.com/HelioConde/VideoForge-IA/actions/runs/43745321463) aprovou 14 testes de pacote SHA/origem/anti-repetição em runner GHCR, com somente PNGs sintéticos temporários de teste. O scanner **bloqueou corretamente** montagem sem fonte original. [Run 43745436851](https://github.com/HelioConde/VideoForge-IA/actions/runs/43745436851) comprovou que o gatilho `workflow_run` chegou ao renderer, mas verificou artifact de arte ausente e pulou o render. Portanto **o encadeamento de jobs funciona**, mas nenhum MP4 C01-P02 foi gerado. A arte e o underlay continuam pendentes.

## Testes do produtor real por tomada — 15/11/2026

O [run 43749824057](https://github.com/HelioConde/VideoForge-IA/actions/runs/43749824057) concluiu **8/8 testes** de política de custo, origem, chamada única, geração mockada RGB/RGBA e archive SHA, sem inferência real. O job manual pago foi corretamente ignorado (`skipped`). A política vigente continua com custo não autorizado; a referência V2 e o MP4 real C01-P02 permanecem ausentes. O [run anterior 43749686509](https://github.com/HelioConde/VideoForge-IA/actions/runs/43749686509) também passou. As duas execuções e a separação dos testes estão registradas em `ESTADO-ATUAL.md` e `HISTORICO-DESENVOLVIMENTO.md`.

## Resultados de CI do medidor de RGBA / 15-11-2026

[Pack 43758686070](https://github.com/HelioConde/VideoForge-IA/actions/runs/43758686070): 23/23 testes passaram no runner GHCR; `--verify-report` detecta aprovação falsificada. [Preview 43758686035](https://github.com/HelioConde/VideoForge-IA/actions/runs/43758686035): preflight e movimento ThreeCanvas em imagens de fixture aprovados, sem fonte real. [Autonomia 43758686062](https://github.com/HelioConde/VideoForge-IA/actions/runs/43758686062): 70 testes e fila de 40 shots/160 fases aprovados. O bloqueio de âncora V2 e gasto continua em vigor. Nenhuma arte verdadeira C01-P02, relatório de geometria de produção ou MP4 dessa tomada foi gerado.
