# AGENTS.md — VideoForge IA (reconstrução)

## REGRA VISUAL ATUAL DO DORAMA C01-P03 — V5, RESPIRAÇÃO DAS COSTAS E CABEÇA

**VERSÃO ATUAL INTEGRADA À MAIN: C01-P03 V5**, não V4. Ler em ordem [checkpoint do episódio](canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/ESTADO-ATUAL.md), [QA completo V5](canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/QA-C01-P03-V5-2026-11-15.md), [manifesto V5](canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/atuacao-c01-p03-v5-respiracao-costas.json), [direção e princípios da V4](canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/REGRAS-ATUACAO-C01-P03-RESPIRACAO-2026-11-15.md), [manual de animação](docs/MANUAL-PRINCIPAL-ANIMACAO-2D.md). **Não voltar à V4 por falta de contexto.**

A revisão humana da V4 pediu **manter o leve movimento da cabeça e acrescentar respiração sutil nas costas**. Regra de atuação C01: duas tracks, `kael.ombros/translateY` até -1,25px e `kael.cabeca/rotationZ` até -0,32°; jaqueta `mesh.backBreath` original com expansão até 1,05px e elevação até 0,6px, restrita às costas Y857–947, sourcePin da cintura desde Y950 e bordas da gola/laterais fixas. O movimento deve ser uma deformação verdadeira **dos vértices do tecido**, não animação do PNG inteiro. Braço/antebraço/mão direitos apoiados no joelho e **sem transformação global**, bota/perna estáticas; guardas, rei e lanças sem deformação, usando imagem-mãe SHA-verificada como cenário. Não adicionar braços/pés só para aumentar contagem de pixels. **Sem criar novas imagens, sem publicar no YouTube; aprovação visual pendente.**

**Prova técnica atual:** [PR #58](https://github.com/HelioConde/VideoForge-IA/pull/58) integrado à `main`, commit `ae7ca09c3f75ed04498704459a2ac547de810d06`; [main render 43680784142](https://github.com/HelioConde/VideoForge-IA/actions/runs/43680784142) e [TS/testes 43680784182](https://github.com/HelioConde/VideoForge-IA/actions/runs/43680784182) **SUCCESS**, artifact temporário da main `14147374656`, MP4 de 3s SHA-256 `d84361f693f4e1c83b4d5ad7bd7ed55c253044e672fbf80af803ace58b865481`, QA real da respiração das costas `back_visible_in_mp4=true` com máximo 957 pixels H.264 alterados em ROI, gola 24/75, rei/lanças/bota imóveis no limiar. `humanVisualReview=false`, `publishable=false`. Próximo passo: revisão visual da V5, não nova geração. **Cena C12 segue bloqueada por PNGs/ZIPs originais faltantes.**

## REGRA PERMANENTE — CONTINUIDADE DO DESENVOLVIMENTO NA MAIN (LER PRIMEIRO)

**Nunca reiniciar um projeto, cena, vídeo ou rig do zero sem consultar seu checkpoint.** A branch `main` é a fonte de verdade dos trabalhos integrados. Ler obrigatoriamente [protocolo de continuidade](docs/CONTINUIDADE-DO-PROJETO.md), depois `canal/<id>/videos/<video-id>/ESTADO-ATUAL.md`, `HISTORICO-DESENVOLVIMENTO.md` e `estado-atual.json` (se existirem), além do manual principal de animação e dos arquivos de direção relevantes.

**Ao concluir QUALQUER alteração técnica, asset, QA, render, correção ou etapa de vídeo:**
1. Confirmar primeiro os fatos reais: branch, commit da **main** (ou PR ainda não integrado), workflow/run, status, artifacts, hashes e a existência dos arquivos, sem considerar um mero log como MP4 arquivado.
2. Atualizar **na mesma alteração enviada à main** o checkpoint por vídeo, relatando de forma objetiva o que está concluído, o que é apenas teste técnico, pendências, falhas e o **próximo comando/etapa exatos**.
3. Acrescentar um registro datado ao histórico (sem apagar versões) e sincronizar o JSON. Se o merge/push falhar, **não declarar registro na main**; relatar que está somente numa branch.
4. Sempre reutilizar o código, as imagens originais e os rigs já implementados. Não duplicar pipelines ou recriar trabalho por não consultar o histórico.
5. Separar aprovação estética, código testado, MP4 técnico gerado, aprovação humana e MP4 oficial: **são estados diferentes**. Não arquivar segredos ou tokens nesses registros.

**Episódio ativo do dorama:** [checkpoint Alchemy Lab — Conquiste a Princesa EP01](canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/ESTADO-ATUAL.md), [relatório ATUAL C01 V5](canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/QA-C01-P03-V5-2026-11-15.md) e [histórico integral](canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/HISTORICO-DESENVOLVIMENTO.md). **A V5 É A MAIS RECENTE NA MAIN**, PR #58, render/QA 43680784142 **SUCCESS**, artifact `14147374656` e SHA gravado no checkpoint. **C01 tem 2 tracks de ombro/cabeça, malha das costas animada dentro da jaqueta e episódio tem 106 tracks no total**. Cabeça V4 preservada, mão/bota direitos imóveis, rei/coroa e lanças intactos. **Sem aprovação visual humana**; não publicar YouTube. C12 ainda requer 9 PNGs originais. **Não recomeçar roteiro, motor ou imagens.**

## REGRA PRINCIPAL — ARQUIVAR TODAS AS IMAGENS NO GITHUB POR CANAL

**Nenhum gerador VideoForge pode depender somente de artifacts temporários do GitHub Actions.** Sempre que um workflow gerar PNGs (imagem-mãe, referência, camadas RGBA, sprites, olhos, cenários), arquivar os bytes originais em canal/CHANNEL/videos/VIDEO_ID/assets/geracoes/PRODUCER/GITHUB_RUN_ID/ antes de declarar a geração concluída, mesmo que ela ainda não esteja aprovada artisticamente. O histórico de versões fica imutável: nunca sobrescrever arquivos anteriores.

Utilizar os programas videoforge/persist_generated_assets.py e scripts/persistir-imagens-gh.sh. Eles validam PNG e SHA-256, origem de canal/vídeo, limites de tamanho e metadados sem segredos, e criam commit no GitHub. O workflow precisa de permissions: contents: write e checkout com persist-credentials: true. Se o arquivamento ou o push falhar, **marcar a execução como falha**, nunca como produção concluída. Artifacts temporários são apenas cópia de segurança.

**Imagens produzidas fora do runner (ex.: imagem criada no chat do ChatGPT)** requerem uma importação real dos bytes. JSON com SHA, arquivo ZIP apenas preparado ou a exibição de uma imagem no chat não são prova de que o PNG chegou ao GitHub. Verificar a existência e os hashes no repositório antes de informar conclusão. O episódio Alchemy Lab EP01 mantém o bloqueio de NOVA geração: arquivar antigos originais é permitido; produzir novas imagens continua proibido sem autorização explícita.

**Durante revisões visuais, mostrar ao usuário as imagens também no chat**, rotulando referência, rascunho, aprovada ou rejeitada. Arquivamento no GitHub e exibição no chat são obrigações separadas.

## PRIORIDADE MÁXIMA DAS ANIMAÇÕES — MANUAL PRINCIPAL OBRIGATÓRIO

**Antes de produzir, editar, gerar imagens, animar, revisar ou renderizar QUALQUER vídeo, ler integralmente [docs/MANUAL-PRINCIPAL-ANIMACAO-2D.md](docs/MANUAL-PRINCIPAL-ANIMACAO-2D.md).** Esse manual foi definido pelo usuário a partir da pesquisa aprofundada de rig 2D/Three.js/Remotion e **TEM PRECEDÊNCIA SOBRE INSTRUÇÕES CONFLITANTES DE ANIMAÇÃO** em AGENTS.md, README, modelos, prompts, agentes e workflows.

**Contrato obrigatório:** cena-mãe → background reconstruído → PNGs RGBA independentes de personagem/corpo-sem-cabeça/cabeça aberta-fechada/cabelo/roupa/objetos → reconstrução das regiões ocultas → recomposição (diff/QA) → pivôs e malhas reais no Remotion ThreeCanvas → render SWANGLE frame-driven → QA visual → somente revisão/publicação autorizada.

**Proibido tratar movimento de câmera, bob da imagem inteira, sticker de pálpebras por cima do cabelo, deformação do corpo achatado ou vídeo sintético como animação articulada aprovada.** Em personagens animados, somente sprites internos com rig e malha reais; se faltar arte ou aprovação, declarar `pipeline_pendente`. Para piscar, editar a MESMA imagem/cabeça original mudando somente os olhos; preservar os demais pixels e a transparência. Sem novos custos não autorizados, sem modo workflow `private-quota-live`, sem upload automático.

**Precedência:** regra geral nº 1 (tudo pelo programa GitHub e sem publicação não autorizada) + este manual para toda decisão de animação. Instruções antigas abaixo sobre overlay de olhos ou bob devem ser interpretadas como histórico de prévias **LEGADAS E REPROVADAS**; não autorizam repetir tais técnicas no vídeo oficial.


## REGRA DE ENQUADRAMENTOS CINEMATOGRÁFICOS — doramas, anime e narrativas

**Para histórias com múltiplas tomadas, ler [docs/GUIA-ENQUADRAMENTOS-CINEMATOGRAFICOS.md](docs/GUIA-ENQUADRAMENTOS-CINEMATOGRAFICOS.md) antes de solicitar imagens.** Um plano geral não pode ser duplicado 20 vezes como pôster. Alternar conforme o roteiro entre close do rosto, extremo close de olhos, sobre-o-ombro, contraplano, planos médios, detalhes de mãos/objetos e planos de estabelecimento. Expressão e continuidade visual são obrigatórias.

O planejamento é `direcao-cinematografica-planos.json` por vídeo e a API reutilizável `videoforge/cinematic_direction.py`. O gerador `videoforge/production_scenes.py` aceita `--shot-id C12-P01` (quando autorizado); é **uma imagem-mãe nova por ângulo necessário**, da mesma referência canônica, com SHA e recortes RGBA específicos. **Não** usar pan, zoom ou recorte de uma arte ampla como substituto de personagem em close de qualidade. UI/HUD e legendas entram no Remotion, não ficam impressos na arte.

**Não quebrar o Manual Principal:** direção de câmera não equivale a rig real; sem underlays/pivôs/QA `pipeline_pendente`. O caso Alchemy Lab EP01 tem bloqueio expresso de nova geração de imagens e conflito de referências entre visual antigo e quadros aprovados no chat; não remover bloqueio nem mesclar figurinos silenciosamente.

## ESTILO V2 DO DORAMA ALCHEMY-LAB EP01 — sem alterar imagens existentes

Para o episódio **mmorpg-conquiste-a-princesa-ep01**, antes de preparar qualquer tomada, ler [a bíblia visual v2](canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/biblia-visual.md) e o [manifesto SHA das duas referências aprovadas como estética no chat](canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/referencias-cinematograficas-aprovadas-no-chat.json). Kael: cabelo castanho quase preto volumoso, arranhões no rosto, capa vinho rasgada, ombreira metálica. Elara: cabelo loiro dourado, olhos violeta, vestido branco e violeta com bordados dourados. Não usar descrições de cabelo preto/vestido azul de Elara e Kael sem capa/armadura da v1, que foi preservada como histórico.

**A aprovação é da preferência visual; os PNGs originais ainda estão pendentes no GitHub** e os 71 PNGs antigos não foram recortados, alterados nem aprovados na v2. Validar os arquivos por SHA e revisar eixos, iluminação, ocultações e continuidade antes de produzir; nunca liberar rig ou MP4 a partir de referência de estilo. Apresentar a arte existente também diretamente no chat para revisão e distinguir claramente imagens de referência, rascunho e aprovada. O lock de **não gerar novas imagens** deste episódio permanece obrigatório.

## REGRA Nº 1 — Vídeos exclusivamente pelo programa VideoForge-IA no GitHub

**Todo vídeo solicitado como produção oficial deve ser criado pelo fluxo de produção do repositório [HelioConde/VideoForge-IA](https://github.com/HelioConde/VideoForge-IA), executado e rastreável no GitHub Actions.** Esta regra tem prioridade sobre qualquer exemplo, demonstração, script temporário, renderer externo ou solução improvisada.

1. Usar o **programa reutilizável do projeto**, seus modelos, agentes e etapas reais, organizados em `canal/<id>/videos/<video-id>/`. Não criar um gerador paralelo específico de um único vídeo para contornar componentes ausentes.
2. Pesquisa/roteiro → arte consistente por cena → separação de personagens e cenários em camadas → animação → narração → edição/legendas → QA técnico e visual. Executar cada etapa disponível e registrar as que ainda faltam. **Não simular agentes ou artes como se tivessem sido gerados.**
3. Gerar MP4 no runner do GitHub Actions do próprio repositório; registrar workflow, run ID, commit, entrada, manifesto por canal, SHA-256, artefato e relatórios de QA. Baixar ou mostrar a cópia do MP4 é permitido, mas **não** criar/substituir a produção fora do programa.
4. Se faltarem agentes, imagens ou integração do fluxo principal, **parar como `assets_pendentes` / `pipeline_pendente` e explicar a limitação**. Não substituir por desenho vetorial, cartões ou narração sintética genérica e apresentar o resultado como o vídeo oficial solicitado. Previews experimentais podem existir para testar motores, sempre marcadas claramente como **`preview_tecnico_nao_oficial`**.
5. Apenas uma execução verificável do fluxo principal, com materiais realmente gerados e verificados, pode receber o rótulo `video_oficial_do_programa=true`. Render bem-sucedido no GitHub, por si só, **não significa** produção completa pelos agentes.
6. **Sem limite artificial para quantidade de cenas**. Segurança, licenças, orçamento aprovado, duração e QA permanecem obrigatórios. Publicação no YouTube exige autorização e verificação próprias.

**Correção histórica:** o teste *Spy x Family* da execução [43545398967](https://github.com/HelioConde/VideoForge-IA/actions/runs/43545398967) foi renderizado pelo GitHub Actions, mas usou `videoforge.spy_family_animated` e desenhos vetoriais de prévia, **não** o fluxo oficial completo de artes/agentes. É um teste técnico, não produção oficial do VideoForge-IA.

## REGRA OBRIGATÓRIA — cena-mãe → camadas RGBA → rig → montagem

**Para QUALQUER vídeo animado, não basta deslocar a ilustração inteira.** Cada cena deve cumprir:

1. **Cena-mãe original:** gerar e guardar a imagem completa no programa, com SHA-256, ID de canal/vídeo/cena, dimensões, enquadramento, pose, figurino, perspectiva, luz e estilo. É a única referência visual para derivar os recortes dessa cena.
2. **Background reconstruído:** editar A PRÓPRIA cena-mãe para retirar personagens e objetos móveis, preenchendo a parte originalmente escondida. Preservar tamanho, perspectiva, iluminação e coordenadas; não inventar um cenário novo.
3. **Personagens separados:** editar A MESMA cena-mãe para extrair cada personagem/parte que se moverá em PNG **RGBA com transparência alfa real** e na mesma posição/escala. Extrair objetos móveis e foreground separadamente se existirem na cena; não inventar objetos ausentes.
4. **Sem duplicação:** a camada base não pode manter o cabelo/capa/braço/objeto que será desenhado novamente como sprite animável. Restaurar partes encobertas de corpo/cenário antes do movimento. Sobrepor tecido na costura, manter pivôs corretos e rosto-base opaco durante piscadas.
5. **Animação verdadeira:** Remotion/rig movimenta personagem, olhos/cabelo/roupas/objetos isolados, com movimentos sutis naturais e vento quando cabível. Movimento de câmera ou pan **é adicional**, não substituto do rig.
6. **QA fail-closed:** verificar SHA da cena-mãe em todas as camadas, PNG RGBA/transparência real, dimensões, alinhamento, ausência de recortes/duplicações, movimento de partes independentes, olhos, rosto, bordas e costuras em vários quadros, narração e legendas. Se algum componente essencial faltar: `pipeline_pendente`; `rig_animado_aplicado=false`; `video_oficial_do_programa=false`. Nunca declarar vídeo oficial com MP4 de pan.
7. **Sem teto de cenas:** a quantidade vem do roteiro; limites de orçamento de inferência, tempo de execução, licenças e duração são controles **separados**. Não consumir chamadas adicionais sem orçamento autorizado.
8. **Local de execução:** usar exclusivamente os módulos reutilizáveis do `HelioConde/VideoForge-IA` e GitHub Actions. Guardar assets e QA por canal/cena, publicar artifacts de revisão, nunca publicar no YouTube sem aprovação.

Ver `docs/PADRAO-ANIMACAO-POR-CAMADAS.md` e `docs/TESTE-CAMADAS-CENA.md`. O exemplo da capa vermelha foi um experimento de rig para outra cena: jamais reutilizar automaticamente seus prompts de aventureiro, cabelo castanho, espada ou capa em outros personagens.

## [LEGADO — NÃO USAR EM PRODUÇÃO] Regra antiga de microanimação e QA visual

Evitar flutuação: amplitude vertical máxima de **2,8 pixels por personagem** na composição 1080×1920; câmera e objetos mais sutis que a animação principal. Piscar somente com overlay RGBA de pálpebras compatível com a cena-mãe, mantendo cabeça/rosto-base opacos; nunca fingir piscada via transparência do rosto. Cabelo, roupas e objetos exigem sprites próprios e prova de remoção da base; não inventar elementos nem afirmar rig completo quando só há movimento de grupo/câmera. Testar quadros de olhos abertos/fechados e cortes; manter workflow **normal**, nunca o modo `private-quota-live`. Toda prévia sem rig integral é teste técnico não oficial.

## [LEGADO — SUBSTITUÍDO PELO MANUAL] Antigo QA de overlay de olhos

Uma piscada **não pode cobrir a franja** nem criar uma mancha de pele sobre cabelo, sobrancelhas ou acessórios. A imagem de olhos fechados gerada por IA é somente material bruto: restringir sua máscara alfa à área exata dos olhos da cena-mãe, excluir todos os pixels classificados como cabelo frontal e colocar a franja REAL extraída do personagem original em **z-index maior** que o sprite de pálpebras. A ordem de composição é `background -> personagem RGBA original -> olhos-fechados-SEGUROS -> franja-original-foreground -> objetos independentes reais -> legendas`. Não habilitar `eyesClosed` sem `hairForeground` validado, SHA de origem correspondente, QA dos pixels e avaliação visual. O cabelo desenhado no personagem-base pode ser usado no foreground somente sem movimento independente até existir underlay e rig próprios; não duplicar cortes móveis.

## Correção prioritária da piscada — editar a MESMA imagem inteira (substitui adesivos)

A partir desta revisão, para vídeos novos, a piscada NÃO deve ser construída por um sticker de olhos ou sobreposição de pele. **Enviar exatamente o `character-main.png` original da cena-mãe ao endpoint de edição de imagem**, com uma única alteração permitida no prompt: **a mesma personagem de olhos fechados**. Cabelo, franja, roupa, rosto, acessórios, pose, escala, cor, iluminação, fundo/transparência e os demais personagens não podem mudar. Gerar uma segunda imagem completa com os olhos fechados, de mesmas dimensões e coordenadas; **alternar entre imagens completas de olhos abertos e fechados**, com o mesmo pivô de animação e sem qualquer overlay.

QA fail-closed: verificar SHA-256 da imagem original de referência, modelo/resultado, dimensões; em seguida restaurar EXATAMENTE os pixels e o canal alfa da imagem original em todas as regiões fora dos olhos (inclusive cabelo e franja). Se a IA devolver PNG opaco, usar só sua informação de cor dentro dos olhos e sempre restaurar o alfa original. Exigir diferença visível exclusivamente nos olhos, nenhum pixel não ocular ou alfa alterado, e revisão visual humana. O pipeline antigo de overlay de pálpebras/cabelo-foreground permanece legado e NÃO é usado nesta nova prévia. Usar GitHub Actions normal, nunca `private-quota-live`. Não declarar aprovação de rig completo.

## [HISTÓRICO — VER MANUAL PRIORITÁRIO] Sincronização antiga de PNG inteiro

A troca `character-main.png` ↔ `character-eyes-closed-safe.png` exige **posição e transformações idênticas** nos dois lados. Nunca reinicializar o seno ou a animação abruptamente no frame da troca. O corpo e todos os elementos anexados devem desacelerar por `12` quadros até a **pose neutra**, mantê-la pelo intervalo de `3` quadros antes/depois do centro da piscada e retomar a respiração de forma suave nos `12` seguintes. Mesmo envelope de neutralização para a câmera: nenhum recorte, zoom, rotação ou deslocamento pode dar um salto nos quadros de transição. Em cada frame de troca: deslocamento X/Y = 0, rotação = 0, zoom = 1, pan = 0 em relação à composição-base. QA testa limites de variação quadro a quadro.

Cabeça e corpo separados só podem ter movimento **independente** quando existirem sprites RGBA reais, corpo **sem a cabeça**, cabeça aberta/fechada consistente e pivot validado; sem estes assets, o vídeo de teste usa microanimação do corpo/conjunto e `independent_head_motion_active=false`. Nunca mostrar falsamente um rig individual. O movimento deve terminar e começar com neutralidade antes/depois dos cortes. Ver `motion-remotion/src/blink-motion-sync.ts`.

## REGRA DE RIG REAL — movimento interno, NÃO PNG inteiro

Quando o usuário solicitar movimento de cabeça, cabelo, roupa, capa, braços ou objetos (como na pesquisa detalhada de 14/11/2026), a implementação oficial deve usar **Remotion ThreeCanvas + malhas reais e partes independentes**. O protótipo de character idle, pan da câmera, zoom, filtros FFmpeg e o movimento de personagem achatado são apenas prévias legadas, nunca satisfazem o requisito de rig articulado.

1. **Arte canônica:** usar cena-mãe, background limpo, corpo sem cabeça, cabeça aberta/fechada, mechas e tecido/objetos SEPARADOS. Todas as peças RGBA vêm da mesma referência, coordenadas originais e hashes verificáveis.
2. **Animação:** pivô no pescoço, máximo ±2° no MVP, olhos como duas versões da MESMA cabeça com só os olhos alterados, malha 7x9 ou similar com vértices superiores fixos e deformação suave nas pontas. Movimento calculado exclusivamente com useCurrentFrame(), sem useFrame()/requestAnimationFrame, relógio ou física de estado acumulado.
3. **Transições:** quadro de troca possui pose/pivô iguais. Easing para neutro e retorno gradual, evitando salto perceptível.
4. **QA:** render de pose neutra deve recompor a arte original com tolerâncias e inspeção visual; SHA, RGBA, bbox, z-index, ausência de duplicação de rosto/capa/cabelo e revisão humana são obrigatórios. Se faltar qualquer sprite ou QA, rig pendente, vídeo não oficial.
5. **Runner:** nova imagem pré-compilada GHCR rig-three-remotion4-v1, workflow normal do GitHub Actions com --gl=swangle --concurrency=1 e sem modo private. Preservar runner e workflows legados isolados para não comprometer produções anteriores.
6. **Não inventar assets:** não aplicar capa/espada de aventureiro em Anya ou outros personagens que não os possuam. O smoke 43580456827 usa figuras sintéticas e **não** é vídeo de canal. O primeiro vídeo real com este motor somente após gerar e validar head/body/hair/props da cena 01.

Ver documentação: docs/RIG-THREE-MALHA.md. O modelo permanece operacional=false até QA real do vídeo por malha.

## Instruções obrigatórias para cada tarefa

**Ler nesta ordem, antes de pesquisar ou produzir qualquer vídeo:** `README.md`, `AGENTS.md`, `docs/ARQUITETURA.md`, `docs/REGRAS-EDITORIAIS.md`, `canal/README.md`, `canal/<id>/README.md`, **`canal/<id>/ESTRATEGIA.md`**, `canal/<id>/canal.json`, histórico e reservas do canal e, se útil, `docs/referencias/CATALOGO-CURSOS-YOUTUBE.md` e `docs/referencias/GUIA-OFICIAL-YOUTUBE-CREATORS.md` (para pesquisa, Analytics, SEO, Shorts, direitos, classificação infantil e IA) e **`docs/CODEX-PROXY-ACTIONS.md` antes de qualquer trabalho envolvendo ferramentas de IA, Go ou Actions**.

**Hierarquia com precedência:** a estrutura canônica é **`canal/` no singular**, conforme `docs/ARQUITETURA.md`. Não criar `canais/` alternativo. Separar rigorosamente canais; dados do vídeo em `canal/<id>/videos/<video-id>/editorial.json`, manifesto renderizável em `video.json`, índice de histórico em `canal/<id>/editorial/historico-videos.json`. Não substituir o formato técnico do manifesto. Conferir histórico e temas relacionados antes de criar nova pauta. Não presumir que o índice inicial vazio comprova ausência de vídeos no YouTube.

Ler `docs/referencias/GUIA-OFICIAL-YOUTUBE-CREATORS.md` como síntese **de fontes oficiais consultadas**, e revalidar os links originais quando decisões envolverem regras atuais. Antes de qualquer publicação futura, checar duração e Content ID em Shorts de mais de um minuto, originalidade contra conteúdo massificado/repetitivo, direitos, classificação infantil e eventual obrigação de declarar uso de IA. Nenhuma dessas instruções habilita publicação no MVP.

Os cursos listados são **fontes sugeridas para estudo**, não prova de acesso, aprendizado ou método validado. Não inventar conteúdo das aulas. Não registrar geração, QA ou publicação sem evidências.

## Integração central com Codex Proxy\n\nTodas as integrações futuras de pesquisa, roteirização e imagens devem usar o gateway definido em `docs/CODEX-PROXY-ACTIONS.md`, sem instalar Go ou clonar o upstream em cada workflow. A imagem do proxy é compilada uma vez em build isolado no GHCR; jobs posteriores usam serviço persistente ou contêiner pré-compilado. O modo efêmero não persiste tokens OAuth renovados, logo não é a opção principal. Nunca imprimir ou versionar `CODEX_PROXY_ACCOUNTS_JSON`, `CODEX_PROXY_API_KEY` ou `CODEX_PROXY_BASE_URL` privado; credenciais somente via GitHub Actions Secrets. Não habilitar geração paga em push/PR; `health` não gera imagens e `generate` é disparo manual único. Se upstream privado mudar, falhar com erro verificável, jamais tentar contornar limites 429. Geração não equivale a aprovação visual nem MP4.\n\n## Autenticação do projeto antigo: migração local

A cópia antiga usa o Environment `proxy-runtime`, mas os valores de Secrets não podem ser recuperados por API. O script `scripts/migrar-codex-proxy.ps1`, para uso **local no Windows**, importa o `accounts.json` existente no Docker ou em arquivo privado e registra os novos Secrets via stdin no `gh` CLI. Nunca armazenar tokens, senhas, chaves, dumps ou arquivos de conta em commits, logs, discussões, PRs, artifacts ou GitHub Pages. Não afirmar que houve migração até ela ser executada localmente e verificada em Actions. Consulte `docs/CODEX-PROXY-ACTIONS.md`.

## Testes de separacao generativa por camadas

Antes de modificar ou executar rotinas de edicao de cenas, leia `docs/TESTE-CAMADAS-CENA.md`. Os workflows `scene-layers-basic.yml` e `scene-layers-advanced.yml` executam somente por `workflow_dispatch`, reutilizam o mesmo PNG original verificado por hash, usam o proxy Go PRECOMPILADO e limitam no maximo 2 imagens por run, sem retry automatico. Resultados vao exclusivamente para `output/<canal>/videos/<video-id>/assets/<cena>/` como artifacts; nunca sao versionados, enviados ao YouTube ou classificados como animacao pronta. O manifesto tem `human_visual_approval=false`, `pixel_alignment_verified=false` e `animation_implemented=false` ate verificacao adequada. Uma edicao por IA NAO e recorte fiel e nao pode substituir QA humano.

## Prévia de animação de camadas verificável

O workflow manual `animate-separated-layers.yml` consome somente o artifact do Teste 2, sem chamadas ao proxy, sem reinstalação de Go/FFmpeg e sem upload ao YouTube. O motor `videoforge/animate_layers.py` anima 3 camadas independentes via FFmpeg, verifica SHA-256, RGBA real, movimento entre quadros e codecs do MP4. A capa e demais peças que ainda existem no personagem-base **não podem ser adicionadas como overlays**, pois isso duplicaria roupa/objetos. É obrigatório criar personagem-base sem a peça e pivôs revistos antes do rig. `modelos/camadas-animadas` permanece desabilitado para produção completa. Ver `docs/ANIMACAO-CAMADAS.md`.

## Motor Remotion reaproveitado do projeto antigo

Para prévias animadas de PNGs, usar como **primeira escolha** a composição React em `motion-remotion/src/scene-layer-preview.tsx` e o [guia](docs/REMOTION-ANIMACAO.md). Os módulos `character-idle.ts`, `cinematic-motion.ts` vieram do `AutoEditorVideo/motion-remotion` fixado em `ec85db5bc74455122e4501aba05bd2dd3fd0df2c`, e `videoforge-motion.ts` do antigo VideoForge. A renderização é executada no workflow `remotion-animate-layers.yml` usando imagem GHCR de Node/Remotion/Chrome já compilada, sem npm ci ou download do navegador a cada job. FFmpeg somente gera silêncio e verifica codecs/quadros. Validar SHA, RGBA e identidade do canal antes de compor, **não duplicar a capa**, não fingir rig de membros/cabelo, não enviar ao YouTube. Modelo `camadas-animadas` ainda não é produção pronta.

## Rig 2D de malha (opt-in, nao aprovado para producao)

Ler [docs/RIG-MALHA-2D.md](docs/RIG-MALHA-2D.md) antes de preparar sprites ou alterar `motion-remotion/src/mesh-rig.tsx`. O rig SVG so pode ser ativado com cinco sprites RGBA sem partes duplicadas, hashes vinculados a cena e `human_review` verdadeiro **apos** revisao real. Nao usar `character-main.png` no mesmo modo de render que `body-no-head-no-cape.png` e `cape.png`. Validacao automatica nao prova qualidade visual; manter `publishable=false` e `visual_review=pending` ate revisar MP4. A existencia de codigo nao significa que os PNGs ou o artifact de rig ja existam. Nao executar inferencia IA nem upload por conta propria.

## Preparacao do rig candidato por cena (sem aprovacao automatica)

Consultar [docs/PREPARAR-RIG-CANDIDATO.md](docs/PREPARAR-RIG-CANDIDATO.md) e `canal/<id>/videos/<video-id>/rig-plan.json` antes de alterar máscaras. `videoforge/rig_candidate.py` **nao** executa SAM2/LaMa nem reconstrói anatomia escondida; apenas gera recortes e previews de risco. Na cena piloto o desenho inclui **segundo olho parcialmente visível** e capa frontal/traseira; separar as partes evita duplicações. Sempre manter `human_review=false` no rascunho; não renomear seu artifact para `rig-...` nem alimentar o workflow de MP4 final sem correção de arte, checagem de oclusão e aprovação humana. O workflow `rig-candidate.yml` não chama API de IA nem publica vídeos.

## Regra permanente — não limitar cenas por número

Nunca acrescentar `MAX_SCENES`, faixas como `3 <= len(scenes) <= 24`, ou checagens exigindo exatamente 10 cenas nos geradores de vídeo. O número de cenas é consequência do **roteiro e dos cortes visuais necessários**, não um teto arbitrário. Validar que a lista é não vazia, caminhos e conteúdo de cada cena, direitos, tempo final do formato, QA e uso de recursos; jamais truncar ou descartar cenas automaticamente para caber em número máximo. Dividir trabalhos em lotes técnicos quando necessário preservando a ordem e o conteúdo, sem limitar o número total de cenas. Orçamento de geração de imagens, quotas de APIs, timeout e limites de duração do Shorts permanecem controles separados e não podem ser burlados.

## Padrão universal da animação de personagens

Antes de desenhar, separar sprites, montar rig ou renderizar personagens de **qualquer canal**, leia [`docs/PADRAO-ANIMACAO-POR-CAMADAS.md`](docs/PADRAO-ANIMACAO-POR-CAMADAS.md). A regra geral é: base do rosto sempre opaca durante a piscada; cabelo e roupas separados apenas quando houver underlay e sobreposição nas costuras; junções ancoradas nos ombros/pescoço; movimento determinístico de corpo, cabelo, roupa e câmera sem fendas, duplicação ou esticar a cabeça. Todo vídeo exige continuidade entre cenas, QA de quadros e aprovação visual. A prévia vetorial de Spy x Family prova apenas o motor: **não** tratá-la como ilustração final ou publicação.

## Objetivo inicial

**No MVP técnico**, comprovar MP4 vertical do Otaku Multicena com 90–180 segundos, áudio audível e QA. **Na produção oficial**, usar exclusivamente o programa integrado no GitHub, com agentes/etapas reais, ilustrações e mídia comprovadas. Validar o renderizador não equivale a gerar vídeo final pelo programa.

## Regras de execução

- O comando smoke usa mídia sintética para testar tecnologia; **jamais**
  registrar esse clipe como produção realizada por agentes.
- O comando render só usa mídia real explicitamente fornecida;
  não inventar identidade de personagem, fontes ou artefatos.
- Sem upload para YouTube e sem chamadas pagas de IA nesta etapa.
- Jamais adicionar credenciais, respostas privadas, imagens geradas,
  áudio de produção ou MP4s ao Git.
- Registrar origem, orçamento e autorização antes de integrar provedores
  de imagem, voz ou pesquisa; não contornar 429 com repetição cega.
- Manter QA fail-closed; qualquer falha de áudio, duração, resolução
  ou integridade bloqueia declaração de vídeo concluído.
- Alterar código em branch/PR e verificar CI antes de integrar.
- Não tocar no repositório antigo. Organizar arquivos por canal,
  preservar documentação e não introduzir agentes visuais fictícios.

## Regra de execução sem instalações repetidas

Os workflows de produção devem reutilizar imagens GHCR pré-compiladas. Usar `ghcr.io/helioconde/videoforge-media-runner:ubuntu2404-ffmpeg-v2` para renderização e o proxy pinado do `docs/CODEX-PROXY-ACTIONS.md` para IA. Nunca reinstalar Go, FFmpeg ou serviços em cada job de vídeo; builds/atualizações são feitos só nos workflows de infraestrutura, com cache e tags estáveis. Runners hospedados ainda precisam baixar a imagem, pois não persistem disco entre execuções. Toda troca de imagem exige smoke real H.264/AAC com QA.

## Validação

    python -m unittest discover -s tests -v
    python -m videoforge.mvp smoke --output dist/smoke.mp4

Conferir artefato de Actions: video H.264, áudio AAC, 1080 × 1920 e QA JSON.
Esse teste não autoriza vídeo público nem consumo de IA.

## Organização permanente — mesmo contrato do VideoForge anterior

Sempre consultar `README.md`, `docs/ARQUITETURA.md` e
`docs/ESTRATEGIA_SHORTS.md` antes de editar ou planejar Shorts.
O guia de Shorts é orientação **editorial**, não autorização para novos jobs,
provedores pagos, pesquisa privada ou publicação.
A estrutura do repositório anterior `HelioConde/video-forge-ia2` é a
referência **apenas para organização**, sem copiar credenciais, pipelines
complexos nem trabalhos fictícios.

- Cada canal vive exclusivamente em `canal/<id>/`; seus dados não podem
  migrar nem ser misturados com os de outro canal.
- Em `canal/<id>/`, manter `canal.json`, `README.md`, 
  `conteudos/indice.json`, `editorial/candidatos.json`,
  `editorial/reservas.json` e `videos/README.md`.
- Pesquisas com fontes ficam em `editorial/pesquisas/YYYY-MM-DD.json`.
  Pastas de arquivo editorial têm valor histórico, **não são fila de produção**.
- Cada vídeo real usa `canal/<id>/videos/<video-id>/video.json`. O modelo
  técnico padrão vem de `canal.json.modelo_padrao`, com sobrescrita opcional
  em `video.json.modelo`; modelos reutilizáveis em `modelos/<id>/modelo.json`.
- Geradores específicos de nicho podem viver em `geradores/<id>/` somente
  quando houver implementação e testes reais; não inferir trabalho ativo a
  partir de arquivos de configuração.
- Manter resultados e dados temporários em `output/<id>/editorial/` ou
  `output/<id>/videos/<video-id>/`, nunca versionados.
- O MVP só processa `otaku-br` e `imagem-estatica` fornecida. O modelo
  `camadas-animadas` está **planejado, não implementado**. 
- `videoforge/paths.py` deve falhar antes de gerar mídia se o canal,
  diretório, receita técnica ou destino de saída estiverem incorretos.
- Em toda mudança: organizar antes e depois, atualizar docs,
  testar regressões, verificar Actions; nunca editar outros repositórios,
  gastar IA ou publicar YouTube sem autorização explícita.

## Diagnosticar rig sem aprovar sprites

Para ver movimento antes de reconstruir partes ocultas, o workflow `rig-draft-preview.yml` produz MP4 **com marca d'água de rascunho** e quadros de revisão. O módulo `videoforge/rig_draft_preview.py` deve aceitar somente `rig-candidate` com `human_review=false`, SHA validado e origem/canal corretos; nunca converter rascunho em aprovação ou publicar o vídeo. Marcar `publishable=false` e registrar inpainting pendente no QA. A versão de produção segue exigindo `validate_rig_dir` com aprovação visual humana.
