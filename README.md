# VideoForge IA — reconstrução orientada a MP4

**Filtro EP01 V2 de figurinos:** [reprovações detalhadas de Aldric (inversão vermelho/preto e barba), Elara (corpete roxo) e checklist de Kael](canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/RELATORIO-APROVACAO-REPROVACAO-FIGURINO.md). Fonte: diferenças reportadas pelo proprietário; sem alegar medição automática de cor por pixel. O roteiro tem 40 tomadas, nenhuma aprovação visual ou publicação automática.

**Dorama EP01 V2 — nova revisão de figurinos:** [Aldric e Elara em comparação ampliada](canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/REVISAR-DETALHES-FIGURINOS-V2.md) e [contrato de continuidade das 40 tomadas](canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/REGRAS-FIGURINOS-V2-40-TOMADAS.md). O antigo registro de 37 tomadas é histórico. Não gerar R2 nem vídeo com trajes reprovados. Não há aprovação automática de identidade.

**Dorama MMORPG EP01 — revisão de figurinos:** [ver 6 referências existentes de Aldric e Elara](canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/REVISAR-OPCOES-FIGURINO-V2.md). A prancha V2 anterior foi reprovada por diferenças de roupas; as referências estão em revisão, não são canônicas. Nenhuma nova imagem R2 foi solicitada ou gerada.

**EP01 V2 — revisão visual de identidade (16/11/2026):** os três PNGs originais de Kael, Elara e C12-P02 estão SHA-verificados. [Comparar personagens e prancha V2](canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/REVISAR-IDENTIDADE-EP01-V2.md) antes de autorizar rig/animação: [Kael](canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/QA-KAEL-V2-COMPARACAO.jpg) | [Elara](canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/QA-ELARA-V2-COMPARACAO.jpg). As prévias são apenas para QA, não aprovam o novo desenho. O MP4 final e a publicação continuam pendentes.

> **AUTORIZAÇÃO DE CHAMADAS DO EP01 V2 — 15/11/2026:** o responsável autorizou permanentemente as chamadas de IA/imagem necessárias ao remake, sem pedir confirmação por imagem; `autonomy-policy.json` permite um gasto de geração por execução do produtor e não define teto editorial total. O coordenador reserva e solicita automaticamente a primeira candidata `character-bible` uma vez, com registro durável e sem repetição cega. A existência de autorização **não** comprova que a API respondeu, que houve cobrança, que alguma arte foi aprovada nem que um vídeo foi publicado. YouTube segue bloqueado.

> **Rig da espada: QA de geometria por pixels reais adicionado.** `remake_rig_geometry.py` e os workflows de pacote/preview exigem relatório `mask-geometry.qa.json` revalidável para C01-P02, com máscara, centroide, SHA e quatro poses. O restante dos 39 planos ainda depende de arte própria; não foi criado MP4 oficial nem liberado custo.

> **Abertura original do remake V2:** `videoforge/remake_episode_audio.py` prepara a mesma WAV por síntese procedural + SHA auditado para o futuro vídeo integral; independe da retenção de 90 dias dos artifacts. O render oficial continua bloqueado pelos 39 planos visuais sem QA.

> **Direção animada V2 disponível:** [40 tomadas e 160 ações temporizadas](canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/remake-v2-motion-directions.json), com câmera, elenco, rig, fases e QA por plano; validador `videoforge/remake_motion_directions.py` e integração à fila dos agentes. **São instruções**, não PNGs/MP4 gerados. Sem rig/autorização visual/custo não renderiza vídeo oficial.

> **Compositor V2 corrigido para 40 tomadas:** [EDL editorial oficial](canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/remake-v2-cinematic-edl.json) · `videoforge/remake_v2_edl.py` · `motion-remotion/src/cinematic-timeline.ts`. O legado 37-shot permanece intocado. A abertura preta exige o áudio original no render do episódio. Aguardando assets reais e revisão.

> **Plano V2 agora com 40 tomadas (14 cenas, 163s):** [manifesto ativo](canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/remake-ep01-planos.json) · [roteiro atualizado](canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/roteiro.json) · [direção oficial](canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/REMAKE-EP01-PLANO-OFICIAL.md). Três novos inserts: C01-P05, C08-P04, C12-P04. Existem 39 tomadas visuais planejadas, mas não foram geradas imagens adicionais nem liberados custos.

> **C01-P02:** novo produtor `videoforge/remake_sword_source.py` + `remake-sword-component.yml` prepara underlay RGB e três peças RGBA por tomada verdadeira, com gate de custo e apenas execução manual. A automação de pacote e render já está ligada; ainda **sem âncora V2 aprovada/sem PNGs finais/sem MP4 da tomada**. [Documentação da fonte/rig](docs/C01-P02-PACOTE-ARTE-E-RIG.md).

> **C01-P02:** empacotamento de arte por SHA e gatilho de render autônomo conectados em `remake-sword-pack.yml` → `remake-sword-preview.yml`. [Pacote e requisitos técnicos](docs/C01-P02-PACOTE-ARTE-E-RIG.md). Fonte V2 e underlay ainda ausentes: sem novos PNGs nem MP4 da tomada.

> **EP01 C01-P02:** prévia articulada agora tem entrada própria no Remotion + validação SHA/PNG/recomposição com FFmpeg (decodificação de PNG para QA) e Python stdlib (composição de pixels): [pacote de arte e rig](docs/C01-P02-PACOTE-ARTE-E-RIG.md). O preflight de GitHub Actions não gera PNG e só libera render com fonte real e referência V2 aprovada.

> **Reutilizacao de bibliotecas e skills:** [catalogo integrado](docs/BIBLIOTECAS-E-SKILLS-VIDEOFORGE.md) · [direcao do remake](.agents/skills/videoforge-dorama-remake/SKILL.md) · [rig Three.js](.agents/skills/videoforge-rig-2d-three/SKILL.md) · [QA e memoria](.agents/skills/videoforge-qa-and-checkpoint/SKILL.md). Novos geradores devem consumir a fila `videoforge/remake_starter.py`, o `remake_autopilot.py` e componentes ThreeCanvas ja instalados. Nenhum novo gasto/MP4 foi habilitado.

> **INTEGRAÇÃO DE CENAS DO REMAKE V2:** o workflow de imagens agora separa o EP01 remake do caminho legado, exige tomada específica e confere o PNG de referência aprovado no próprio GitHub por SHA + manifesto. Essa ligação de software **não cria imagens automaticamente** nem dá autorização para serviços pagos ou YouTube.

> **AUTONOMIA DO VIDEOFORGE (15/11/2026):** [manual de operação autônoma](docs/AUTONOMIA-PRODUCAO-VIDEOS.md) · [coordenador verificável](videoforge/remake_autopilot.py) · [workflow diário](.github/workflows/remake-autonomy.yml). A meta é o programa produzir e corrigir os vídeos por si, enquanto damos direção editorial. O primeiro módulo já diagnostica o próximo passo e atualiza o checkpoint; o encadeamento completo de imagens, rigs, QA e MP4 ainda precisa ser integrado e testado. **Não tratar planejamento como vídeo gerado, nem chamar API paga sem permissão.**

> **REMAKE EP01 ATIVO (15/11/2026):** [plano de refação](canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/REMAKE-EP01-PLANO-OFICIAL.md) · [manifesto das 40 tomadas](canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/remake-ep01-planos.json) · [checkpoint obrigatório](canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/ESTADO-ATUAL.md). **Geração de novas artes autorizada editorialmente para o remake**, sem cota artificial, preservando V5/C12 anteriores como legado. O lock de 14/11 foi arquivado, não está mais ativo. Ainda não existem novas imagens, rig aprovado ou MP4 oficial do remake; não gastar serviços externos nem publicar sem permissão específica.

> **REGRA NOVA DE QUALIDADE DO DORAMA (15/11/2026):** sem teto editorial de imagens — quando autorizadas, criar quantos ângulos, imagens-mãe, camadas e refinamentos forem necessários para uma animação bonita, detalhada e consistente. **Antes e depois de todo avanço, consultar e atualizar o arquivo mestre [ESTADO-ATUAL.md](canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/ESTADO-ATUAL.md)**, sincronizando [histórico](canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/HISTORICO-DESENVOLVIMENTO.md) e [JSON](canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/estado-atual.json). Não perder o progresso nem refazer etapas concluídas. **O usuário autorizou posteriormente refazer o EP01 com novas imagens (remake V2)**; o bloqueio anterior está arquivado. Esta mudança documental não gera mídia, não concede orçamento e não autoriza publicação.

> **NOVO PADRÃO VISUAL EXCLUSIVO DO DORAMA / Alchemy Lab:** [área dorama](canal/alchemy-lab/dorama/README.md) · [prompt oficial — Cinematic Semi-Realistic Fantasy Anime](canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/PROMPT-OFICIAL-ESTILO-DORAMA.md) · [manifesto JSON](canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/estilo-visual-oficial-dorama.json) · [amostra em miniatura](canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/REFERENCIA-VISUAL-DORAMA-PREVIEW-96.jpg). Quase toda cena deverá ser dramática e filmada de ângulo diferente, com continuidade de rostos, armaduras, luz e arquitetura. **Regra editorial aplicada ao remake autorizado em 15/11/2026:** o lock anterior é histórico, não vigente. O registro da política isoladamente não produz render, geração ou publicação.

> **CONTINUIDADE OBRIGATÓRIA NA MAIN — NÃO RECOMEÇAR DO ZERO:** antes de trabalhar, ler [AGENTS.md](AGENTS.md) e o [protocolo de continuidade](docs/CONTINUIDADE-DO-PROJETO.md), depois o `ESTADO-ATUAL.md` e o `HISTORICO-DESENVOLVIMENTO.md` do vídeo. **Cada conclusão/alteração precisa atualizar esses arquivos na mesma integração à `main`**, com run, commit, artifact, SHA, pendências e próximo passo. Branches antigas e chats não substituem esse registro. Episódio ativo: [dorama MMORPG — checkpoint e MP4s técnicos C01/C12](canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/ESTADO-ATUAL.md).


> **ATUAL — C01-P03 V5 (15/11/2026):** [relatório do movimento das costas e QA real](canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/QA-C01-P03-V5-2026-11-15.md) · [manifesto V5](canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/atuacao-c01-p03-v5-respiracao-costas.json) · [checkpoint](canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/ESTADO-ATUAL.md). [PR #58](https://github.com/HelioConde/VideoForge-IA/pull/58) **integrado na main**, commit `ae7ca09c3f75ed04498704459a2ac547de810d06`; [render + QA main #43680784142](https://github.com/HelioConde/VideoForge-IA/actions/runs/43680784142) e [TS/testes #43680784182](https://github.com/HelioConde/VideoForge-IA/actions/runs/43680784182) **SUCCESS**. **Respiração suave das costas em malha RGBA original** (até 1,05px expansão / 0,6px elevação), **cabeça continua mexendo levemente** (máximo 0,32°); braço/mão/joelho/pé direitos travados, rei/coroa e lanças estáticos com pixels originais. MP4 3s/90f/1080×1920/30fps SHA-256 `d84361f693f4e1c83b4d5ad7bd7ed55c253044e672fbf80af803ace58b865481`, artifact temporário `14147374656` idêntico ao PR. **QA técnico aprovado, aprovação artística humana pendente; sem geração de imagens, sem YouTube.** V4/V3 são checkpoints **históricos**, não a versão ativa.

> **C01-P03 V4 — direção corrigida pelo usuário em 15/11/2026:** [pesquisa de bibliotecas e skills](docs/PESQUISA-SKILLS-BIBLIOTECAS-RIGGING-2D-2026-11-15.md) · [regras de animação — somente respiração](canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/REGRAS-ATUACAO-C01-P03-RESPIRACAO-2026-11-15.md) · [roteiro técnico de atuação V4](canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/atuacao-c01-p03-v4-respiracao.json) · [PR #57](https://github.com/HelioConde/VideoForge-IA/pull/57). **A V3 passou QA técnico, mas foi rejeitada visualmente:** braço direito afastava-se do apoio, pé ficava cortado, lanças ruins e cabeça do rei incompleta. A V4 trabalha com 2 tracks leves de respiração e cabeça, mão/bota ancoradas em mundo e rei/lanças da imagem-mãe original, sem gerar imagens novas. **V4 integrada à main (PR #57, commit `4d010a92212ce77e9c7fbcf762537ecf0e732be2`):** [render/QA 43676630976](https://github.com/HelioConde/VideoForge-IA/actions/runs/43676630976) **SUCCESS**; [relatório permanente V4](canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/QA-C01-P03-V4-2026-11-15.md). MP4 técnico de 3s/90f/1080×1920, SHA `90baea03b4e2b551a21d341c263853a2e9b9d4d5647314fff46a39bf79fbbff7`. **Aprovado tecnicamente, NÃO visualmente nem para YouTube.**

> **DORAMA ALCHEMY LAB — C01-P03 V3 EM MAIN (15/11/2026):** [Checkpoint atualizado](canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/ESTADO-ATUAL.md) · [relatório técnico completo, inclusive tentativas reprovadas](canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/QA-C01-P03-V3-2026-11-15.md) · [histórico permanente](canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/HISTORICO-DESENVOLVIMENTO.md). [PR #56](https://github.com/HelioConde/VideoForge-IA/pull/56) integrado, [render da main 43673610507](https://github.com/HelioConde/VideoForge-IA/actions/runs/43673610507) **SUCCESS** com MP4 técnico de 3 s/1080×1920/90 frames (SHA-256 `73993ab7b1f93aead42d1860d16c3db965adcbd3e6bdf2794eb631a9d704100c`). **Movimento real 18.923 ≥16.000 e exposição da gola 73 ≤75: gates técnicos passaram; a aprovação visual não.** O rig usa nove trilhas independentes nesse plano, 113 no episódio, cabeça ≤1,82°, proteção de gola feita somente de pixels originais, nenhum novo desenho. **Pendências:** recomposição neutra ainda com erro RGB ≈11,16, recortes de guardas/lanças/Aldric, inspeção de bota/mão e demais planos; C12 bloqueada por PNGs originais. **Não publicar no YouTube.**

> **ARQUIVAMENTO AUTOMÁTICO DE IMAGENS:** imagens produzidas pelos geradores do GitHub devem ser preservadas permanentemente em canal/ID/videos/ID/assets/geracoes/PRODUCER/RUN_ID/, com SHA-256 e manifesto. Os artifacts do Actions, com prazo de expiração, não são o arquivo definitivo. **[Guia e recuperações verificadas de PNGs antigos](docs/ARQUIVAMENTO-PERMANENTE-IMAGENS.md)**. A implementação reutilizável está em videoforge/persist_generated_assets.py e scripts/persistir-imagens-gh.sh. Os jobs de arte, cenas, lotes, sprites e imagens manuais devem commitar os PNGs antes de reportar sucesso. As imagens criadas fora do runner (ChatGPT) ainda exigem importação dos bytes: referências catalogadas no chat não são PNGs já arquivados. O bloqueio de novas imagens do episódio Alchemy Lab EP01 permanece inalterado.


> **MANUAL PRINCIPAL DE ANIMAÇÃO 2D (OBRIGATÓRIO PARA TODOS OS CANAIS):** [Leia primeiro o manual de malha Three.js + Remotion](docs/MANUAL-PRINCIPAL-ANIMACAO-2D.md). Ele tem prioridade sobre regras antigas de bob/câmera/pálpebras em overlay. Nenhuma animação oficial deve ser classificada como rig articulado quando apenas o PNG inteiro se move. Exigir cena-mãe, partes RGBA independentes, reconstrução de regiões ocultas, rig por pivôs/malhas, comparação com arte original, QA e aprovação. **Sem sprites reais completos, manter como pipeline pendente.**

> **ECONOMIA DE TOKENS (Codex CLI):** [Configuração econômica inicial](.codex/config.toml) e [guia com pesquisa da comunidade](docs/ECONOMIA-CODEX-ASTRA.md). Usar Sol para manutenção normal, Astra Standard somente por escalada; não ativar Ultrafast por padrão. **Isso não modifica o Codex Proxy, não gera imagens e não autoriza novos custos**. O manual principal de animação mantém precedência.

> **LEITURA OBRIGATÓRIA (antes de qualquer tarefa):** [AGENTS.md](AGENTS.md) → [Arquitetura das pastas](docs/ARQUITETURA.md) → [Regras editoriais dos vídeos](docs/REGRAS-EDITORIAIS.md) → [Regras do canal](canal/README.md) → **[Estratégia específica do canal](canal/README.md#estratégias-específicas-por-canal) e `canal/<id>/ESTRATEGIA.md`** → [Cursos de referência](docs/referencias/CATALOGO-CURSOS-YOUTUBE.md) → [Guia oficial YouTube Creators](docs/referencias/GUIA-OFICIAL-YOUTUBE-CREATORS.md) → [Infraestrutura Codex Proxy](docs/CODEX-PROXY-ACTIONS.md).
>
> **Prioridade absoluta:** preservar a estrutura existente **`canal/<id>/`** (singular), `modelos/`, `geradores/`, `videoforge/`, `tests/` e `docs/`. Cada vídeo tem seus dados e histórico dentro de seu próprio canal; não criar `canais/` nem misturar informações entre canais. Cursos de YouTube são **referências para estudo**, não aulas já assistidas. A análise oficial do YouTube Creators está registrada com fontes e ressalvas; políticas devem ser revalidadas antes de publicar.
>
> Esta organização mantém o MVP apenas como **teste técnico**. Vídeo oficial exige o fluxo real e integrado do programa (agentes, arte, animação, voz, edição, QA e proveniência no GitHub); nenhuma prévia substitui essa integração. Sem publicação automática ou IA paga nesta etapa.

## Regra nº 1 — Vídeos exclusivamente pelo programa VideoForge-IA no GitHub

**Todo vídeo solicitado como produção oficial deve ser criado pelo fluxo de produção do repositório [HelioConde/VideoForge-IA](https://github.com/HelioConde/VideoForge-IA), executado e rastreável no GitHub Actions.** Esta regra tem prioridade sobre qualquer exemplo, demonstração, script temporário, renderer externo ou solução improvisada.

1. Usar o **programa reutilizável do projeto**, seus modelos, agentes e etapas reais, organizados em `canal/<id>/videos/<video-id>/`. Não criar um gerador paralelo específico de um único vídeo para contornar componentes ausentes.
2. Pesquisa/roteiro → arte consistente por cena → separação de personagens e cenários em camadas → animação → narração → edição/legendas → QA técnico e visual. Executar cada etapa disponível e registrar as que ainda faltam. **Não simular agentes ou artes como se tivessem sido gerados.**
3. Gerar MP4 no runner do GitHub Actions do próprio repositório; registrar workflow, run ID, commit, entrada, manifesto por canal, SHA-256, artefato e relatórios de QA. Baixar ou mostrar a cópia do MP4 é permitido, mas **não** criar/substituir a produção fora do programa.
4. Se faltarem agentes, imagens ou integração do fluxo principal, **parar como `assets_pendentes` / `pipeline_pendente` e explicar a limitação**. Não substituir por desenho vetorial, cartões ou narração sintética genérica e apresentar o resultado como o vídeo oficial solicitado. Previews experimentais podem existir para testar motores, sempre marcadas claramente como **`preview_tecnico_nao_oficial`**.
5. Apenas uma execução verificável do fluxo principal, com materiais realmente gerados e verificados, pode receber o rótulo `video_oficial_do_programa=true`. Render bem-sucedido no GitHub, por si só, **não significa** produção completa pelos agentes.
6. **Sem limite artificial para quantidade de cenas**. Segurança, licenças, orçamento aprovado, duração e QA permanecem obrigatórios. Publicação no YouTube exige autorização e verificação próprias.

**Correção histórica:** o teste *Spy x Family* da execução [43545398967](https://github.com/HelioConde/VideoForge-IA/actions/runs/43545398967) foi renderizado pelo GitHub Actions, mas usou `videoforge.spy_family_animated` e desenhos vetoriais de prévia, **não** o fluxo oficial completo de artes/agentes. É um teste técnico, não produção oficial do VideoForge-IA.

**Estado atual:** há renderizadores de testes técnicos, mas a produção oficial ainda exige integrar pesquisa, agentes, modelos de imagem, animação, voz e QA ao fluxo principal. Não classificar MP4 experimental como trabalho concluído do gerador. O repositório
anterior, agora `HelioConde/video-forge-ia2`, permanece intacto e serve
somente como referência para organização.

## Estratégia editorial de Shorts

Os materiais de crescimento/SEO enviados em 2026-11-13 foram sintetizados
em [Estratégia de YouTube Shorts](docs/ESTRATEGIA_SHORTS.md), que inclui
pesquisa, antirrepetição por canal, retenção, consistência visual,
métricas e fontes oficiais atualizadas. **Leia o guia antes de planejar**;
essas práticas ainda não são automações implementadas.

## Infraestrutura IA: Codex Proxy e Actions\n\nO componente central planejado de IA é [10/chatgpt-codex-proxy](https://github.com/10/chatgpt-codex-proxy). Os workflows manuais [build de imagem do proxy](.github/workflows/proxy-image.yml) e [teste/geração de imagem](.github/workflows/proxy-images.yml) usam imagem Docker precompilada ou um serviço HTTPS com sessão persistente, sem reinstalar Go em todo job. **Confira o passo a passo de secrets e os limites** em [docs/CODEX-PROXY-ACTIONS.md](docs/CODEX-PROXY-ACTIONS.md). Esta infraestrutura não significa que credenciais já foram configuradas, imagem foi gerada ou publicação foi habilitada.\n\n## Ferramentas de mídia reutilizadas nos workflows

O workflow [MVP MP4](.github/workflows/mvp.yml) usa a imagem pré-compilada `ghcr.io/helioconde/videoforge-media-runner:ubuntu2404-ffmpeg-v2`, com Python 3.12, FFmpeg 6.x e fontes. O build fica isolado em [media-image.yml](.github/workflows/media-image.yml); cada job faz apenas pull da imagem, **não** reinstala Go, Python ou FFmpeg. O Codex Proxy tem sua imagem separada.

## Aproveitar as contas do Codex Proxy anterior

Para migrar a sessão já autorizada do contêiner Docker antigo sem novo login no Codex, o [script local de migração](scripts/migrar-codex-proxy.ps1) envia o estado privado aos Secrets do novo repositório pelo `gh` CLI. Consulte [as instruções e limitações](docs/CODEX-PROXY-ACTIONS.md). Secrets antigos do GitHub não podem ser lidos de volta pela API.

## Testes de decomposicao de cena com IA (separados do MVP)

Os workflows [Teste 1 - background e personagem](.github/workflows/scene-layers-basic.yml) e [Teste 2 - foreground e objetos animaveis](.github/workflows/scene-layers-advanced.yml) usam **a mesma cena-base** obtida no artifact do Codex Proxy. A geracao e manual e limitada a no maximo 2 edicoes de imagem por run; PNGs e manifesto ficam somente em artifacts organizados por canal. Consulte o [guia de testes de camadas](docs/TESTE-CAMADAS-CENA.md). A edicao e generativa: transparencia tecnica nao garante recorte fiel, coordenadas ou animacao pronta.

## Prévia animada das camadas em MP4 (sem IA)

O [Teste 3 de animação](.github/workflows/animate-separated-layers.yml) usa os PNGs de background, personagem e telhado obtidos pela separação para criar uma prévia parallax de 6–10 segundos com **movimentos independentes**. O motor `videoforge/animate_layers.py` verifica o artifact, renderiza H.264/AAC e confere movimento real entre quadros. **A capa isolada ainda não é usada** porque permanece dentro do sprite completo e seria duplicada; o vídeo é técnico, sem narração e sem envio ao YouTube. [Instruções](docs/ANIMACAO-CAMADAS.md).

## Remotion original — nova prévia animada por camadas

O motor **principal para a nova prévia** é agora [Remotion do AutoEditorVideo](motion-remotion/): reutilizamos as funções do projeto anterior em uma composição React que movimenta camera, personagem e foreground por frame. O novo [workflow manual Remotion](.github/workflows/remotion-animate-layers.yml) usa os PNGs dos artifacts reais com validação de SHA-256, renderiza MP4 com H.264/AAC e QA de movimento, **sem gastar IA ou instalar npm/Chrome toda vez**. Consulte [guia do Remotion](docs/REMOTION-ANIMACAO.md). O renderizador antigo de parallax FFmpeg permanece somente como teste/fallback documentado; a capa não é sobreposta até remover sua versão duplicada do personagem.

## Preparacao visual do rig com pixels da cena original (rascunho)

A nova etapa de [preparação dos sprites](docs/PREPARAR-RIG-CANDIDATO.md) usa o artifact original verificado para produzir **seis camadas candidatas**, separando a capa em frente e trás e reconhecendo os dois olhos parcialmente visíveis. O workflow `rig-candidate.yml` gera máscaras, contact sheet, hashes e proveniência **sem IA e sem publicar**. Os recortes ainda não reconstroem anatomia escondida e permanecem bloqueados para uso como rig aprovado.

## Rig 2D por malha — implementacao opt-in (ainda sem sprites aprovados)

O novo [MVP de rig 2D](docs/RIG-MALHA-2D.md) acrescenta ao Remotion um **warp por triangulos da capa**, **pivo da cabeca no pescoco** e **piscadas em quadros definidos**. O codigo e validadores existem; a ativacao depende de cinco PNGs RGBA sem partes duplicadas, hashes e revisao visual humana. Sem rig, o workflow permanece no modo legado; **nao existe ainda MP4 real aprovado deste modo novo**. Nao habilita publicacao nem o modelo `camadas-animadas` para producao.

## Regra permanente: sem teto de quantidade de cenas

**O gerador não deve impor limite fixo de cenas** (nem 10, 24, 30 ou outro valor arbitrário). Roteiros, manifestos e renderizadores devem aceitar qualquer número **positivo** de cenas válido, determinado pela narrativa. O motor renderiza e valida cena a cena, sem reduzir, mesclar, cortar ou descartar cenas apenas por terem ultrapassado uma contagem pré-definida.

Esta regra não remove o QA, a exigência de assets reais, as verificações de direitos, a segurança contra abuso, o orçamento autorizado de IA, os limites operacionais do GitHub Actions nem a **duração** do formato. Por enquanto o piloto Shorts do Otaku BR permanece com 90–180 segundos; se a narrativa não couber, deve ser adaptada ou planejada para formato mais longo, não ter cenas apagadas automaticamente. Mudanças no número de cenas não significam publicação ou geração de IA automática.

## O que já funciona

- Compositor FFmpeg de **imagens e narrações fornecidas**, com legendas,
  MP4 H.264/AAC vertical 1080 × 1920.
- QA automático de vídeo, áudio, duração, resolução e SHA-256.
- Smoke test no GitHub Actions produz clipe técnico sintético de ~5 segundos
  (não é vídeo editorial, não é produção de agentes, sem IA paga).
- Produção do primeiro Otaku Multicena exige **90–180 segundos**
  e a autorização humana para qualquer integração futura de IA.
- Não há publicação no YouTube, nem credenciais no Git.

## Pastas — igual ao VideoForge anterior

```text
canal/
  otaku-br/                         # Otaku Multicena, piloto
    canal.json                      # opções / modelo padrão
    conteudos/indice.json           # referências, não fila automática
    editorial/
      candidatos.json               # pesquisas autenticadas futuras
      reservas.json                 # antirrepetição, começa vazio
      pesquisas/YYYY-MM-DD.json     # futuro, só pesquisa verificável
    videos/
      <video-id>/video.json         # manifesto por vídeo
  otaku-en/                         # Otaku Reframe
  gamer/                            # Conde Games
  manu-kids/                        # Emanuelly Kids
  alchemy-lab/                      # Alchemy Lab
modelos/
  imagem-estatica/modelo.json       # implementado: imagens fornecidas
  camadas-animadas/modelo.json      # PLANEJADO, ainda não implementado
geradores/                          # receitas de nicho futuras
videoforge/                         # código reutilizável
tests/                              # testes offline e FFmpeg
docs/ARQUITETURA.md                 # regra permanente de organização
output/
  <channel>/videos/<video-id>/      # MP4 e QA; ignorado pelo Git
```

Confira [regras dos canais](canal/README.md),
[modelos](modelos/README.md) e
[arquitetura](docs/ARQUITETURA.md).

**Isolamento:** nenhum vídeo, métrica, pauta ou reserva de um canal pode ser
usado como se fosse de outro. O código valida canal e modelo, e bloqueia
o destino de saída fora de seu diretório.

## Executar

Requer Python 3.12+ e FFmpeg/FFprobe no PATH, sem dependências Python extras.

```bash
python -m unittest discover -s tests -v
python -m videoforge.mvp smoke --output dist/smoke.mp4
```

Após fornecer **mídia realmente existente** e o manifesto aprovado:

```bash
python -m videoforge.mvp render --video canal/otaku-br/videos/episodio-001/video.json
```

Esse comando gera o arquivo e relatório QA em:
`output/otaku-br/videos/episodio-001/video.mp4` e
`output/otaku-br/videos/episodio-001/video.qa.json`.

O manifesto `video.json` tem este formato **ilustrativo**:

```json
{
  "schema": "videoforge/mvp/v1",
  "channel": "otaku-br",
  "modelo": "imagem-estatica",
  "youtube_upload": false,
  "scenes": [
    {"image": "imagens/cena-01.png", "audio": "voz/cena-01.mp3", "caption": "Legenda 1"},
    {"image": "imagens/cena-02.png", "audio": "voz/cena-02.mp3", "caption": "Legenda 2"},
    {"image": "imagens/cena-03.png", "audio": "voz/cena-03.mp3", "caption": "Legenda 3"}
  ]
}
```

Os arquivos de imagens e voz devem existir ao lado de `video.json` nos
respectivos subdiretórios, mas **não são versionados**. A narração somada
precisa durar 90–180 segundos. O manifesto de exemplo **não contém mídia
nem aprova a escolha do tema**.

`modelo` é opcional no vídeo e usa por padrão `canal.json.modelo_padrao`.
O Otaku Multicena tinha `camadas-animadas` como padrão provisório no antigo
projeto; nesta reconstrução usa `imagem-estatica` **temporariamente** para
entregar um MP4 real primeiro. O modelo de camadas ainda está desativado.

## Próximos marcos

1. Preservar o MP4 técnico aprovado pelo CI após organização por canal.
2. Renderizar vídeo de 90–180s com áudio e imagens reais, sem falar em
   agentes até haver evidências dos trabalhos deles.
3. Só depois implementar pesquisa, três agentes independentes,
   provedores de IA com limites, identidade visual e animações.
4. YouTube Analytics, QA editorial e publicação são etapas separadas;
   nunca enviar conteúdo automaticamente.

**QA técnico não é aprovação editorial ou visual.**

## Rig de direção cinematográfica — C01

A [animação por direção](docs/ANIMACAO-POR-DIRECAO.md) usa o motor real ThreeCanvas/Remotion para executar pivôs, hierarquia de peças e keyframes do roteiro com PNGs originais. O [manifesto de C01-P03](canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/direcao-bindings-c01-draft.json) e o [workflow](.github/workflows/directed-rig-preview.yml) reproduzem uma prévia técnica de 3 segundos da cena do trono e arquivam MP4 e evidências em GitHub Actions.

**Importante:** a prévia possui arte ainda não aprovada, máscaras e underlays pendentes e marca de rascunho. Não é o episódio completo nem autoriza geração de imagens ou publicação. O C12 tem [pré-voo de fontes separadas](canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/RENDER-C12-TECNICO.md) e permanece bloqueado até importar seus originais.
