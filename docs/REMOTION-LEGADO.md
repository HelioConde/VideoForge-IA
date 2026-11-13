# Infraestrutura Remotion reaproveitada do projeto AutoEditorVideo

Origem oficial do usuario: https://github.com/HelioConde/AutoEditorVideo/tree/ec85db5bc74455122e4501aba05bd2dd3fd0df2c/motion-remotion

Modulos reutilizados **sem alteracao de algoritmo**:
- `motion-remotion/src/character-idle.ts`: respiracao/idle por camada separada.
- `motion-remotion/src/cinematic-motion.ts`: movimentos cinematicos de camera.
- `motion-remotion/src/videoforge-motion.ts`: coreografia de camada/cues criada no VideoForge anterior, a partir do fluxo Fofinho, preservada como modulo independente.
- `motion-remotion/package.json`, `package-lock.json`, `tsconfig.json`: dependencia Remotion/React da revisao fixada ec85db5bc74455122e4501aba05bd2dd3fd0df2c; lockfile resolve Remotion v4.0.539.

A imagem `ghcr.io/helioconde/videoforge-remotion-runner:legacy-ec85db5-v1` e construida pela pipeline `.github/workflows/remotion-image.yml` apenas quando dependencias ou Dockerfile mudam na branch `main`, ou por execucao manual. Node 22, Python 3, FFmpeg e Chrome Headless Shell (do proprio Remotion) ficam preinstalados. Jobs posteriores so baixam a imagem precompilada e executam o render, **sem npm install nem npx remotion browser ensure por job**.

Proxima etapa: incorporar composicao e runner para os PNGs reais da cena do Otaku Multicena, com QA tecnico e sem publicar YouTube. O FFmpeg pode permanecer como ferramenta auxiliar de mux/QA, mas o **movimento** sera criado pelo Remotion. Nada neste documento significa que um novo MP4 Remotion ja foi gerado.

Referencias oficiais:
- https://www.remotion.dev/docs/docker
- https://www.remotion.dev/docs/cli/render
- https://www.remotion.dev/docs/license/pricing (conferir licenciamento conforme o uso).
