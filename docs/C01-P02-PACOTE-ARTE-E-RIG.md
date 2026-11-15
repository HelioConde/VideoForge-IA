# C01-P02 — contrato de produção da espada no GitHub

**Data:** 15/11/2026. **Regra:** `AGENTS.md` → `docs/MANUAL-PRINCIPAL-ANIMACAO-2D.md` → `remake-ep01-planos.json` → esse contrato. Nunca substituir a imagem-mãe pelo pôster V1 ou inventar PNGs. Prévia técnica ≠ vídeo oficial.

## Origem, tomada e arte

- Canal: `alchemy-lab`; vídeo: `mmorpg-conquiste-a-princesa-ep01`; cena/tomada `C01-P02`.
- O trecho ocupa **frames globais 60–149** (3 segundos, 90 frames a 30 FPS).
- Espada pertence ao **carrasco**, mão enluvada. Macro/insert de mão, lâmina e bainha, sem rostos. Direção `remake-ep01-planos.json`.
- Fonte obrigatória: **uma imagem-mãe 1024×1536 da própria C01-P02**, derivada da âncora V2 de personagens aprovada, com `scene-mother.production.json` do produtor `videoforge/production-scene/v1` (campos `shot_id`, `number=1`, `reference_sha256`, `sha256`). Referência antiga de outro enquadramento é recusada.
- Camadas independentes de mesmo canvas: **`underlay.png`** (fundo reconstruído e opaco), **`sheath.png`**, **`blade.png`**, **`hand.png`** (RGBA com transparência verdadeira). A recomposição em pose neutra precisa reproduzir o RGB da imagem-mãe, com MAE automática máxima 0,5; revisão de costuras, máscara e anatomia escondida continua humana.
- Pivô `wristPivot=[x,y]` **medido na mão da arte**; `draw` contém `beginFrame`, `finishFrame`, `travelPx`, `axisDeg`, `handFollow`, `handRotationDeg`. Ajustar pelas proporções reais; valores de código de teste não são medidas da arte.

## Artifact consolidado de origem

Para usar o fluxo quando as imagens reais estiverem disponíveis, um empacotador/agente deve reunir os arquivos sob um único artifact do GitHub Actions com nome `vf-remake-c01-p02-sword-source-<run_id>`. Esse mesmo `run_id` entra no `sword-bundle.json` e na entrada manual do workflow. **O empacotamento automático de múltiplos artifacts de geração ainda é etapa pendente.**

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
