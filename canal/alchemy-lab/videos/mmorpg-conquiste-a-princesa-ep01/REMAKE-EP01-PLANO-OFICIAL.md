# REMAKE EP01 — PLANO OFICIAL (15/11/2026)

> **C01-P02 com renderizador técnico pronto para fontes reais:** `motion-remotion/src/remake-sword-preview-index.ts` + `videoforge/remake_sword_preview.py`. Contrato de quatro camadas e origem auditável: [docs/C01-P02-PACOTE-ARTE-E-RIG.md](../../../../docs/C01-P02-PACOTE-ARTE-E-RIG.md). Sem referência V2 aprovada o CI deve permanecer bloqueado, não inventar assets ou declarar vídeo completo.

## Base reutilizavel de bibliotecas e skills (15/11/2026)

**Novo:** catalogo [Bibliotecas e skills](../../../../docs/BIBLIOTECAS-E-SKILLS-VIDEOFORGE.md), 3 skills locais de agente, fila deterministica de 40 tomadas em `videoforge/remake_starter.py` e primeiro movimento de espada independente em `motion-remotion/src/remake-sword-rig.tsx` + `remake-sword-motion.ts`. Sao componentes do proprio programa e nao uma imagem inventada. Os agentes devem priorizar essas bases e documentar toda etapa no checkpoint; nao substituir engine e nao contornar autorizacoes de arte/custo/YouTube.

> **Integração técnica nova:** a direção do remake V2 passou a ser a fonte selecionada por `videoforge/cinematic_direction.py` e por `videoforge/production_scenes.py`. O código valida a ordem, o elenco, a câmera e a âncora visual por SHA antes de geração. **Não existe PNG, rig ou MP4 novo** desta alteração; o usuário ainda precisa aprovar a âncora e qualquer consumo pago de provedor.

**Estado:** preprodução ativa, autorizada editorialmente pelo pedido de refazer o EP01 e "Continuar". **Nenhum PNG, rig, MP4 ou render novo foi executado nesta atualização.** O bloqueio anterior foi preservado no arquivo histórico, não está mais ativo. Novas gerações são permitidas segundo autorização e condições operacionais; não há limite editorial de imagens, mas continuam proibidos gastos adicionais não aprovados e publicação no YouTube.

## Regra nova: autonomia do VideoForge (15/11/2026)

**O objetivo não é ChatGPT consertar cada etapa manualmente.** O PROGRAMA no GitHub deve tomar o roteiro e o manifesto, decidir o próximo estágio, chamar seus workflows existentes, verificar os resultados reais, corrigir automaticamente **somente falhas determinísticas seguras**, revalidar e persistir o avanço no arquivo principal. Nossa intervenção deve servir para **orientar estilo e objetivo**, não para executar cada desenho ou rig. Ler [política de autonomia](../../../dorama/README.md) e o módulo `videoforge/remake_autopilot.py`. Não inventar autonomia concluída: o primeiro módulo é coordenador/diagnóstico e só poderá liberar geração quando acesso/custos e referências estiverem válidos. Erros de identidade/copyright/aprovação humana exigem escalonamento, nunca autoaprovação.

## Direção e cinematografia

**Direção técnica animável (40 tomadas):** `remake-v2-motion-directions.json` contém 160 etapas temporizadas, quatro por tomada, identificando câmera, elenco, peças RGBA e regras de QA. Não são valores inventados de rig em pixels: `source_geometry_calibration_required=true`, todos os pivôs continuam pendentes da imagem-mãe real e `approved_for_final_render=false`. `videoforge/remake_motion_directions.py` valida cada etapa contra `roteiro.json` e `remake-ep01-planos.json`; `remake_starter.work_queue` incorpora essas instruções à tarefa enviada aos agentes. Para a espada C01-P02 usar fases locais `0,7,72,89`, para os olhos de C12-P01 `0,4,86,119`. A fila NÃO autoriza chamada paga nem render oficial.

**Renderizador V2 40 tomadas:** `motion-remotion/src/cinematic-timeline.ts` valida 40 e as janelas dos três inserts. `remake-v2-cinematic-edl.json`, compilada por `videoforge/remake_v2_edl.py`, lista direção, elenco, tempos, falas, HUD, câmera e áudio de 40 tomadas; **39 continuam sem arte aprovada**. A EDL antiga `timeline-cinematografica.json` de 37 é apenas referência histórica. C01-P01 agora possui áudio obrigatório no compositor: antes do render integral, recuperar/recriar o WAV original e conferir SHA da QA técnica C01-P01. O manifesto V2 editorial não libera render oficial.

**Validação do programa:** [run 43751714168](https://github.com/HelioConde/VideoForge-IA/actions/runs/43751714168) SUCCESS (45 testes, fila 40/39); [run 43751714070](https://github.com/HelioConde/VideoForge-IA/actions/runs/43751714070) SUCCESS (14 testes do pacote). Nenhum PNG/MP4 oficial novo e custo bloqueado.

**Decisão editorial de 15/11/2026:** o usuário definiu **40 tomadas cinematográficas, mantendo as 14 cenas**. A mudança aumenta em apenas três imagens-mãe mínimas (39 planos visuais; um plano preto) e **não altera o episódio de 163 s/4.890 frames/30fps**. Foram desdobrados C01-P04 (novo C01-P05: pressão das lanças, frames 310–359), C08-P03 (novo C08-P04: roda e fuga, 2880–2939) e C12-P03 (novo C12-P04: broche, 4290–4349). A tomada especial **C01-P02 continua 60–149**, sem mudar a mecânica do rig da espada. História, eventos, identidades e política de custo permanecem inalterados. **Não houve três novas gerações de imagens, nem mudança automática para aprovação ou publicação.**

Manter **14 cenas, 40 tomadas oficiais e 163 s/4890 frames**, com liberdade para novos ângulos e refinamentos quando a narrativa exigir. Visual oficial **Cinematic Semi-Realistic Fantasy Anime**; personagens idênticos entre planos, roupas e objetos coerentes, luz e arquitetura consistentes. A referência original de 864×1536 ainda não está salva em resolução plena no GitHub, só miniatura 96×171; não fingir que ela é um PNG-mãe aprovado.

Fatos que não podem mudar: a espada da abertura é do carrasco, Kael está ajoelhado no julgamento, guardas seguram lanças coerentes com as mãos, a princesa Elara só é revelada como tal em C12. HUD, legendas e texto ficam no Remotion, nunca na arte-mãe.

## Cadeia automática desejada

`roteiro/planos → identidade visual âncora → imagem-mãe por tomada → arquivamento com SHA → background + sprites RGBA + underlays → QA recomposição → rig de ossos/malhas Three.js → preview Remotion SWANGLE → QA real do MP4 → registro mestre → próxima tomada → episódio completo → revisão humana → publicação somente autorizada`.

Antes de produzir qualquer ativo, os agentes leem **ESTADO-ATUAL.md**, **estado-atual.json**, **HISTORICO-DESENVOLVIMENTO.md**, manifesto e assets da `main`. Depois de cada execução material devem escrever resultados reais, falhas, caminhos, hashes e próxima ação. Não recomeçar de V1 nem repetir gerações cujo SHA foi verificado. Limites por execução podem existir por segurança; **não são um limite editorial total de imagens**.

## Cenas do episódio

| Cena | Evento | Duração | Planos |
|---|---|---:|---|
| C01 | Prólogo: lâmina e julgamento | 12s | C01-P01, C01-P02, C01-P03, C01-P04, C01-P05 |
| C02 | Acusação | 12s | C02-P01, C02-P02 |
| C03 | Memória | 7s | C03-P01, C03-P02 |
| C04 | Último login | 13s | C04-P01, C04-P02, C04-P03 |
| C05 | Nível um | 14s | C05-P01, C05-P02, C05-P03 |
| C06 | Mercado | 11s | C06-P01, C06-P02 |
| C07 | Desconhecida | 13s | C07-P01, C07-P02, C07-P03 |
| C08 | Carrinho | 16s | C08-P01, C08-P02, C08-P03, C08-P04 |
| C09 | Separação | 10s | C09-P01, C09-P02 |
| C10 | Broche | 12s | C10-P01, C10-P02 |
| C11 | Prisão | 13s | C11-P01, C11-P02, C11-P03 |
| C12 | Olhar de lado | 12s | C12-P01, C12-P02, C12-P03, C12-P04 |
| C13 | Conquiste a princesa | 10s | C13-P01, C13-P02 |
| C14 | Noivado falso | 8s | C14-P01, C14-P02, C14-P03 |

## Plano por tomada

| Tomada | Frames absolutos | Técnica | Direção dramática | Separação/rig exigidos |
|---|---|---|---|---|
| C01-P01 | 0–59 | black | Preto absoluto, som do aço; nunca chamar IA de imagem | preto e SFX, sem imagem |
| C01-P02 | 60–149 | insert | Espada pertence ao carrasco; mão, bainha e lâmina separadas | objeto e mãos separados, pivôs e contato físico |
| C01-P03 | 150–239 | low_angle | Kael ajoelhado, leve respiração das costas e cabeça, mão e bota fixas | personagens independentes, respiração/cabelo/tecido |
| C01-P04 | 240–309 | wide | Lanças cruzadas por dois guardas ATRÁS de Kael, trono ao fundo, Elara AUSENTE | cenário em camadas, atores e adereços independentes |
| C01-P05 | 310–359 | insert | Macro das luvas dos dois guardas apertando as lanças cruzadas atrás de Kael; sem Elara | duas hastes, mãos e pivôs independentes; salão com underlay |
| C02-P01 | 360–569 | close_up | Close frontal da face do rei Aldric, coroa e barba nítidas, olhos severos; fundo do trono muito desfocado. | cabeça/olhos/cabelo, boca se há fala, pescoço reconstruído |
| C02-P02 | 570–719 | close_up | Close lateral 3/4 do rosto ferido de Kael, cabeça ainda baixa, sobrancelhas contraídas, olhos mirando chão. | cabeça/olhos/cabelo, boca se há fala, pescoço reconstruído |
| C03-P01 | 720–809 | extreme_close_up | Macro de olhos e pupila de Kael; reflexo azul dentro da íris, rosto real opaco e franja coerente. | pupila/pálpebras originais, olhos em camadas, piscar |
| C03-P02 | 810–929 | match_cut | Match cut entre olho e monitor com duas imagens próprias | duas artes-mãe separadas conectadas por corte, sem morph |
| C04-P01 | 930–1049 | over_shoulder | Da altura do ombro de Kael no computador; lateral do rosto, mão no mouse e teclado legíveis; luz azul. | foreground e personagem em foco com oclusão real |
| C04-P02 | 1050–1169 | insert | Tela do monitor como detalhe de objeto; a mensagem de erro deve ser interface separada no Remotion, jamais texto pintado. | objeto e mãos separados, pivôs e contato físico |
| C04-P03 | 1170–1319 | medium | Câmera lateral vê luz azul nas mãos e no rosto de Kael que tenta proteger os olhos; não mudar anatomia. | tronco, cabeça, mãos, cabelo/capa com rig |
| C05-P01 | 1320–1469 | close_up | Close de Kael no chão quando abre os olhos; surpresa, poeira, contraste entre rosto e estrada desfocada. | cabeça/olhos/cabelo, boca se há fala, pescoço reconstruído |
| C05-P02 | 1470–1589 | wide | Plano geral de Arken, muralhas e árvores em profundidade; Kael pequeno na estrada, sem rosto dominante. | cenário em camadas, atores e adereços independentes |
| C05-P03 | 1590–1739 | medium | Plano médio 3/4 com Kael fitando o próprio campo de visão, olhos seguindo HUD composto no Remotion. | tronco, cabeça, mãos, cabelo/capa com rig |
| C06-P01 | 1740–1919 | insert | Detalhe das duas mãos de Kael abrindo bolsa vazia; bancas desfocadas ao fundo. | objeto e mãos separados, pivôs e contato físico |
| C06-P02 | 1920–2069 | close_up | Close de reação irônica de Kael à missão secundária; sobrancelha e boca expressivas, HUD separado. | cabeça/olhos/cabelo, boca se há fala, pescoço reconstruído |
| C07-P01 | 2070–2189 | tracking | Elara encapuzada sem revelar que é princesa | marcha/corrida articulada, pés e roupas em malha |
| C07-P02 | 2190–2339 | low_angle | Perspectiva baixa do beco com os dois mascarados surgindo na curva; Elara recua à distância. | personagens independentes, respiração/cabelo/tecido |
| C07-P03 | 2340–2459 | two_shot | Plano curto a dois: Elara pede ajuda com mão estendida, Kael se vira assustado, olhos se cruzam. | dois rigs separados e contato de mãos |
| C08-P01 | 2460–2609 | over_shoulder | Sobre o ombro de Kael, mostrar carrinho de madeira próximo; mão estendida rumo à lateral. | foreground e personagem em foco com oclusão real |
| C08-P02 | 2610–2789 | action | Carrinho e rodas articulados, perseguição no beco | rotação de rodas, braços/objetos com pivôs |
| C08-P03 | 2790–2879 | wide | Plano aberto: carrinho bloqueia caminho, Elara foge por corredor lateral, os mascarados param. | cenário em camadas, atores e adereços independentes |
| C08-P04 | 2880–2939 | insert | Roda do carrinho desacelera enquanto Elara desaparece pelo corredor; perseguidores bloqueados | roda/eixo, pés/capa e fundo com contato real |
| C09-P01 | 2940–3089 | close_up | Close de Elara emocionada e agradecida, uma mão toca a mão de Kael fora de foco. | cabeça/olhos/cabelo, boca se há fala, pescoço reconstruído |
| C09-P02 | 3090–3239 | over_shoulder | Da nuca/ombro de Kael vê Elara encapuzada desaparecer na esquina; ligação espacial do beco preservada. | foreground e personagem em foco com oclusão real |
| C10-P01 | 3240–3389 | insert | Macro de flor prateada se soltando da roupa, jóia no ar antes de cair no solo. | objeto e mãos separados, pivôs e contato físico |
| C10-P02 | 3390–3599 | insert | Detalhe dos dedos indicador e polegar de Kael recolhendo o broche com perspectiva consistente. | objeto e mãos separados, pivôs e contato físico |
| C11-P01 | 3600–3719 | over_shoulder | Sobre o ombro do guarda, foco na mão de Kael exibindo o broche, rosto de Kael em plano secundário. | foreground e personagem em foco com oclusão real |
| C11-P02 | 3720–3869 | close_up | Close lateral do rosto de Kael recebendo acusação, olhar surpreso e lança desfocada no primeiro plano. | cabeça/olhos/cabelo, boca se há fala, pescoço reconstruído |
| C11-P03 | 3870–3989 | wide | Plano geral do portão, guardas limitam passagem de Kael; eixo de 180 graus conservado. | cenário em camadas, atores e adereços independentes |
| C12-P01 | 3990–4109 | extreme_close_up | Pupilas de Kael desviam; cabeça imóvel | pupila/pálpebras originais, olhos em camadas, piscar |
| C12-P02 | 4110–4229 | over_shoulder | Revelação da princesa somente agora; OTS sobre Kael | foreground e personagem em foco com oclusão real |
| C12-P03 | 4230–4289 | close_up | Close de reação de Elara ao reconhecer Kael; olhos e flor prateada reconhecíveis, trono desfocado. | cabeça/olhos/cabelo, boca se há fala, pescoço reconstruído |
| C12-P04 | 4290–4349 | insert | Broche de flor prateada no traje de Elara confirma a pista de C10; revelação somente em C12 | broche, dedos e tecido com máscaras independentes |
| C13-P01 | 4350–4499 | medium | Plano médio do rosto de Kael observando o vazio onde HUD surgirá separadamente; Elara ao fundo. | tronco, cabeça, mãos, cabelo/capa com rig |
| C13-P02 | 4500–4649 | close_up | Close no rosto de Kael e microexpressão de choque, HUD de risco e recompensa em camada Remotion. | cabeça/olhos/cabelo, boca se há fala, pescoço reconstruído |
| C14-P01 | 4650–4739 | medium | Plano médio da princesa descendo um degrau, mão no vestido; rei ao fundo reage. | tronco, cabeça, mãos, cabelo/capa com rig |
| C14-P02 | 4740–4829 | close_up | Elara declara noivado falso, expressão e visemas | cabeça/olhos/cabelo, boca se há fala, pescoço reconstruído |
| C14-P03 | 4830–4889 | extreme_close_up | Olhos de Kael e corte seco para preto | pupila/pálpebras originais, olhos em camadas, piscar |

Campos legíveis por agentes: [remake-ep01-planos.json](remake-ep01-planos.json). Cada uma das 39 tomadas visuais requer arte-mãe própria, camadas e QA; **C01-P01 é preto puro + SFX, sem IA de imagem**. C03-P02 envolve mais de uma fonte, logo a contagem final de imagens não é restrita a 39.

## Primeira fase executável

1. Conferir a identidade canônica de Kael (cabelo escuro, olhos âmbar, capa vinho), Elara (cabelo loiro, olhos violeta, capuz no beco), Aldric (barba grisalha, coroa) e guardas. Criar âncora visual com gerador existente somente se o provedor, custo e autorização técnica estiverem resolvidos.
2. Arquivar PNG e SHA no próprio vídeo e inspecionar a arte; não marcar aprovação humana sem revisão.
3. Produzir C01-P02: espada do carrasco, mão, bainha e lâmina em camadas com pivôs. Depois C01-P03 Kael ajoelhado e C01-P04 guardas cruzando lanças, todos com perspectiva própria e animação articulada.
4. O coordenador deve retomar a partir do primeiro estágio **realmente pendente** e classificar falha como recuperável ou bloqueio de qualidade/autorização, sem loops de geração.

**Checkpoint principal:** [ESTADO-ATUAL.md](ESTADO-ATUAL.md). **Legado:** C01-P03 V5 técnica 3s com QA, C12 com importação pendente; preservar integralmente, não converter em aprovação do remake. `video_oficial_do_programa=false` e `youtube_uploaded=false` até o encerramento completo.
