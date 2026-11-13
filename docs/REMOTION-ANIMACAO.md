# Nova animação por Remotion — reaproveitando o AutoEditorVideo

O novo workflow usa a engine **Remotion 4.0.539** que já estava no projeto antigo, com os módulos copiados da revisão `ec85db5bc74455122e4501aba05bd2dd3fd0df2c` do [AutoEditorVideo](https://github.com/HelioConde/AutoEditorVideo/tree/ec85db5bc74455122e4501aba05bd2dd3fd0df2c/motion-remotion), mais o módulo de cues `videoforge-motion.ts` do [VideoForge anterior](https://github.com/HelioConde/video-forge-ia2/blob/main/videoforge/motion/videoforge-motion.ts). Não altera o repositório antigo.

## Mudança em relação ao teste anterior

O antigo `videoforge/animate_layers.py` renderizava todos os movimentos via filtros FFmpeg. A nova versão **não** usa FFmpeg para movimentar imagens: cada quadro é definido pela composição React/Remotion `motion-remotion/src/scene-layer-preview.tsx`, importando diretamente as funções do motor anterior:

- `motionAtFrame`, de `cinematic-motion.ts`: câmera e enquadramento cinematográficos.
- `characterPoseAtFrame`, de `character-idle.ts`: movimento e respiração de um personagem RGBA isolado.
- `videoForgeMotionAtFrame`, de `videoforge-motion.ts`: coreografia por quadro de camadas separadas; aplicada suavemente ao primeiro plano.

A capa continua **desabilitada** como overlay: seu PNG isolado existe, porém o PNG completo do personagem ainda contém a mesma capa. Sobrepor duas capas geraria erro visual. Este trabalho não contém rig de ossos, rotação de braços, cabelo articulado ou animação labial: serão exigidos sprites e máscaras sem peças duplicadas.

## Pipeline que realmente pode ser executado

Workflow manual: [VideoForge - Teste Remotion legado: animar camadas (MP4)](../.github/workflows/remotion-animate-layers.yml).

Parâmetros padrão do exemplo real, cuja origem pode ser verificada nos GitHub Actions:

- `source_run_id: 43437992955` — run do Teste 2 com `camadas-advanced-otaku-br-teste-proxy-20261113-cena-01-43437992955`
- `channel: otaku-br`, `video_id: teste-proxy-20261113`, `scene: cena-01`
- `duration: 8` segundos; `preset: equilibrado` (do motor Remotion antigo)

O workflow verifica os hashes SHA-256, tipo e alfa reais do PNG, preserva coordenadas e importa só `background.png`, `character-main.png` e `foreground-roof.png` em `motion-remotion/public/vf-scene/`. Gera WAV silencioso local para permitir áudio técnico AAC, cria props JSON e renderiza o MP4 com o **CLI Remotion**, não com FFmpeg. Depois o FFprobe/FFmpeg servem exclusivamente ao QA: H.264, AAC, 1080×1920, duração e diferença entre dois quadros decodificados.

Saída em artifact, não em Git:

```text
output/otaku-br/videos/teste-proxy-20261113/animacoes/cena-01/
    remotion-teste.mp4
    remotion-teste.qa.json
    remotion-props.json
```

Sem roteiro, narração, voz final, legendas, vídeo publicável, APIs de IA ou upload no YouTube. O MP4 contém áudio **silencioso proposital**.

## Dependências já instaladas

- Imagem: `ghcr.io/helioconde/videoforge-remotion-runner:legacy-ec85db5-v1`.
- A imagem é construída separadamente em `remotion-image.yml`, **uma única vez** por mudança de Dockerfile/dependência, com npm ci e `remotion browser ensure` durante o build.
- Nos jobs de animação e de CI, utiliza `node_modules` e Chrome preinstalados: **não** executa npm ci, download do navegador, instalação de Go ou recompilação do proxy.
- A dependência está pinada no lockfile anterior; não usar `latest` nem instalar versões divergentes do Remotion em jobs de produção.
- Existe licenciamento específico para Remotion: consultar https://www.remotion.dev/docs/license/pricing antes de utilização comercial/escala.

## Limites e próximos passos

1. Inspecionar as bordas e a coincidência das camadas ao longo dos quadros. QA técnico não aprova qualidade visual.
2. Gerar e validar corpo/roupa sem capa antes de permitir animação independente da capa, cabelo, braços e espada.
3. Manter o modo `camadas-animadas` com `operacional=false` até existir animação articulada e pipeline de produção completo.
4. Não regenerar imagens desnecessariamente, nem consumir conta Codex para renderização de Remotion.
5. Arquivos do GitHub Actions têm retenção limitada; se o artifact de origem expirar, é necessário recuperar/gerar novamente os assets de forma autorizada.

## Implementacao opcional de malha 2D (fase seguinte)

Foi adicionado [rig 2D SVG](RIG-MALHA-2D.md): deformacao real de triangulos da capa, rotacao discreta da cabeca e piscadas. O modo atual **continua** sem capa extra; o novo modo requer sprites RGBA separados sem duplicacao e revisados, que **ainda nao foram produzidos/aprovados**. Nao confundir implementacao do motor com animacao de personagem ja validada em MP4. O workflow aceita `rig_run_id` opcional, sem IA nem novas dependencias no runner.
