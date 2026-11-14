# Produção com artes reais — VideoForge-IA

## Regra nº 1

Todo vídeo deve ser produzido por módulos **reutilizáveis** em `videoforge/`, modelos e dados em `canal/<id>/videos/<video-id>/`, rodando no GitHub Actions, com evidência de cada etapa. Prévia SVG/cartão, smoke e mídia sintética nunca podem substituir o vídeo oficial.

## Etapas existentes e evidências verificáveis

1. **Prancha de referência artística** — `videoforge/production_art.py`; entrada `production-art.json`; arte PNG real gerada via proxy, no artifact do run [43555226353](https://github.com/HelioConde/VideoForge-IA/actions/runs/43555226353). A prancha é coerente para Loid, Anya e Yor, mas não são sprites separados para rig.
2. **Cenas reais** — `videoforge/production_scenes.py`; utiliza `POST /v1/images/edits` com a mesma prancha autenticada por SHA-256, mantendo identidade; a cena 01 está no run [43555469650](https://github.com/HelioConde/VideoForge-IA/actions/runs/43555469650), e as restantes são processadas pelo workflow `production-scenes-batch.yml` com matriz dinâmica e concorrência máxima de 2. O número de cenas **não possui teto artificial**.
3. **Áudio** — o staging de áudio por cena é originado do VideoForge-IA (run `43545398967`), voz PT-BR sintética offline. É **provisória** e precisa ser substituída por narração mais natural na produção final.
4. **Composição canônica** — `videoforge/production_assemble.py` carrega somente artefatos reais, verifica nomes, SHA-256 da cena, da prancha e do áudio; então chama **`videoforge.mvp.render`**. `.github/workflows/production-assemble.yml` é ativado com sucesso do lote de imagens. Entrega MP4 em `output/<id>/videos/<video-id>/` e QA; não publica no YouTube.
5. **Animação articulada** — **ainda não está integrada às cenas reais**. O motor Remotion do projeto e as regras de rosto opaco, costura com sobreposição, pivôs e vento estão documentados em `docs/PADRAO-ANIMACAO-POR-CAMADAS.md`. O MP4 do compositor canônico com imagens reais é uma versão **para revisão**, não uma afirmação de que houve rig de personagens.
6. **Agentes e aprovação** — o registro `editorial.json` permanece `video_oficial_do_programa=false` e `qa_visual=pending` até integração de arte em camadas, execução dos agentes e revisão real. `videoforge/production_origin.py` protege contra promoção indevida de prévias a produção oficial.

## Política de imagens e continuidade

- Cada imagem é gerada **dentro do GitHub Actions**, pelo cliente Codex Proxy do repositório. Não criar imagens no computador ou substituir por exemplos gerados fora.
- Nesta execução, orçamento máximo de 30 chamadas de imagem; plano de 1 prancha + 16 cenas = **17 chamadas**, e sem retry automático em HTTP 429. O limite de cenas no roteiro não se confunde com orçamento de chamadas de IA.
- Sempre validar que `scene.production.json.reference_sha256` coincide com a prancha e que o PNG tem tamanho e estrutura corretos. QA técnico não prova consistência facial; revisar amostras de todos os trechos.
- Nenhum MP4, imagem, áudio ou credencial é versionado no Git. Arquivos binários ficam no artifact e só seus metadados/hashes no canal.
- Modelo `camadas-animadas` permanece não operacional até a implementação real de sprites, rig e QA; não marcar `operacional=true` sem testar.
- YouTube upload continua desabilitado; somente após revisão editorial, de direitos autorais e visual.

## Vídeo atual

`canal/otaku-br/videos/spy-x-family-familia-de-mentira/`

- Título: “Spy x Family: por que Anya esconde os segredos dos pais?”
- 16 cenas; roteiro e SEO em `roteiro.json` e `editorial.json`.
- Prancha gerada: run `43555226353`.
- Cena 01 gerada: run `43555469650`.
- Lote 2..16: run `43555715519`.
- Os IDs da execução do MP4 final/revisão devem ser registrados **apenas após a conclusão e QA**. Não inventar IDs, arquivos ou estados.
