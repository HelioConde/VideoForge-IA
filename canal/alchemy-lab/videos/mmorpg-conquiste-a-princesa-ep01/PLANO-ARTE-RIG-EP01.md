# Alchemy Lab — Plano de produção, separação e rigs — Episódio 01

**Status verificado (14/11/2026):** roteiro de 163 segundos e 37 planos registrado. Existem 14 imagens-mãe e camadas candidatas; NÃO existe MP4 oficial nem animação integral aprovada. Esta etapa foi executada sem geração de imagens.

## Regra ativa deste pedido

**NÃO GERAR IMAGENS NOVAS.** Proibido invocar modelos de edição, desenho ou geração de imagem, mesmo em background. As ações permitidas são: salvar arquivos existentes, extrair pixels, gerar máscaras a partir desses pixels, validar SHA/alpha, catalogar, alinhar, organizar as pastas, programar o rig e fazer QA. Manter manual global e não publicar no YouTube.

## Estrutura e proveniência por canal

- assets/referencias/character-bible.png — identidade visual gerada anteriormente.
- assets/cenas-mae/cena-01.png ... cena-14.png — 14 quadros originais do gerador, tecnicamente verificados, não todos aprovados artisticamente.
- assets/proveniencia/ — recibos de geração, hashes SHA-256 e manifestos de origem.
- assets/manifesto-arquivo.json — índice dos 18 PNGs arquivados dos artefatos GitHub Actions (46,8 MB).
- assets/cena-01/candidatos/background-reconstructed.png — salão reconstruído, ainda sem QA final de recomposição.
- assets/cena-01/candidatos/character-group-REJECTED.png — contém pixels indevidos do trono; nunca montar diretamente.
- assets/cena-01/candidatos/kael-rgba-candidate.png — recorte independente, porém contaminado por halo; ainda não é rig.
- assets/cena-01/rig-drafts/kael/ — 12 partições de pixels existentes e split-qa.json; uma camada residual de halo rejeitada.
- assets/cena-01/variacoes-geradas-na-conversa/ — destino dos oito PNGs criados anteriormente no chat, ainda sem upload; são variações não alinhadas à cena-mãe.
- uploads/alchemy-lab-imagens-geradas-anteriormente.zip — entrada temporária opcional para importar oito PNGs do chat, se enviado pelo usuário ao GitHub.

## Cronologia da abertura (fonte: direcao-rig-remotion.json)

| Plano | Frames absolutos | Arte, rig e câmera | Estado |
|---|---:|---|---|
| C01-P01 | 0–59 | Preto absoluto e áudio. | Roteiro |
| C01-P02 | 60–149 | Punho, bainha, lâmina e reflexo independentes; máscara real no desembainhar, sem usar as lanças como espada. | Assets inexistentes |
| C01-P03 | 150–239 | Kael ajoelhado, cabeça baixa, ombros/dedos e respiração sutis; reconstruir áreas ocluídas. | Partições rascunho |
| C01-P04 | 240–359 | Dolly-out real do ThreeCanvas revela dois guardas ATRÁS dele; braços e mãos movimentam as lanças até cruzar em X, com SFX no contato. | Lançase guardas sem rigs validados |

## O que será necessário separar

**Kael:** as 12 partições atuais incluem cabelo, rosto/orelha, tronco/jaqueta, dois braços, antebraço e mão direita, duas pernas e duas botas. Elas são máscaras binárias sobre pixels originais. A recomposição dos pixels visíveis passou, mas não existe anatomia oculta reconstruída, pivô medido ou face com olhos visíveis. Para o olhar furtivo da C12, usar uma arte-mãe em ângulo facial adequado; não desenhar olhos na nuca do Kael.

**Rei Aldric:** cabeça e coroa, olhos e sobrancelhas, boca com visemas sincronizados, barba/cabelo, corpo sem cabeça, braços, mãos e manto. O personagem precisa manter posição sentada diante do trono. A imagem criada anteriormente no chat é uma variação de referência, não recorte fiel 1:1 do quadro da cena-mãe.

**Guarda esquerdo e direito:** dois corpos e rigs separados, ombros, braços superiores, antebraços, luvas/mãos, pernas, capacetes e capas em malha. Cada lança é outro sprite e seu pivô deve ser medido na mão do guarda correspondente, com hierarquia de transformações e sem atravessar outro personagem. As ilustrações das duas lanças do chat não devem substituir automaticamente as armas desenhadas na cena-mãe.

**Trono e cenário:** o salão já foi reconstruído; a variação isolada do trono do chat não está alinhada com a mãe e precisa ser tratada como arte candidata, nunca sobreposta diretamente ao trono existente, pois geraria duplicação.

## QA obrigatório, sem atalhos

1. Preservar a cena-mãe completa, dimensões e SHA. Validar alfa RGBA verdadeiro e áreas escondidas.
2. Excluir de qualquer render os arquivos marcados REJECTED. Cenas-mãe 02 e 03 estão reprovadas visualmente porque revelam Elara antes da hora ou colocam Kael em pé.
3. Partição por máscara é somente uma separação de pixels; o relatório split-qa.json confirma recomposição exata dos pixels visíveis e marca explicitamente underlays, rosto, pivôs e limpeza como pendentes.
4. Criar rig.json somente com sprites individuais adequados, medições de bbox/pivô no canvas original e coordenadas compatíveis. Cabelo/capa requerem malha com raízes fixas.
5. Evitar corpo inteiro flutuando, zoom de PNG achatado, olhos adesivados, rostos transparentes e cabelo/capa duplicados.
6. Só então validar animação frame-driven de Remotion 4 + React Three Fiber/ThreeCanvas com swangle; sem useFrame ou física acumulativa.
7. Registrar QA visual humano separadamente dos testes técnicos. Sem render MP4 completo e aprovado, video_oficial_do_programa=false e youtube_uploaded=false.

## Histórico e links dos arquivos já gerados

- Referência: [43590930215](https://github.com/HelioConde/VideoForge-IA/actions/runs/43590930215)
- Cena C01: [43591342058](https://github.com/HelioConde/VideoForge-IA/actions/runs/43591342058)
- Lote C02–C14: [43591745279](https://github.com/HelioConde/VideoForge-IA/actions/runs/43591745279)
- Fundo e recorte conjunto: [43592098806](https://github.com/HelioConde/VideoForge-IA/actions/runs/43592098806)
- Kael RGBA: [43592844393](https://github.com/HelioConde/VideoForge-IA/actions/runs/43592844393)
- Arquivar existentes no canal: [arquivo de execução](https://github.com/HelioConde/VideoForge-IA/actions/workflows/archive-alchemy-existing-assets.yml)
- Particionar Kael existente sem IA: [arquivo de execução](https://github.com/HelioConde/VideoForge-IA/actions/workflows/split-alchemy-existing-pixels.yml)

## Imagens anteriores geradas nesta conversa

Há um ZIP local de oito PNGs (Aldric; dois guardas e duas versões adicionais; duas lanças; trono). Esses arquivos não estavam nos artefatos anteriores do GitHub. A conexão atual do GitHub não aceita cópia direta desses binários do container. Para importar sem gerá-los outra vez, enviar o ZIP existente à pasta uploads/ pelo GitHub. O workflow import-alchemy-existing-chat-assets.yml valida os SHA-256 e move os PNGs para assets/cena-01/variacoes-geradas-na-conversa/, removendo o ZIP intermediário. Até isso acontecer, NÃO afirmar que as oito imagens estão no repositório.

Referência normativa: docs/MANUAL-PRINCIPAL-ANIMACAO-2D.md e AGENTS.md. A direção quadro a quadro permanece no arquivo direcao-rig-remotion.json.


## 7. Nova etapa: guardas individualizados por pixels, sem IA

A execução [43598226488](https://github.com/HelioConde/VideoForge-IA/actions/runs/43598226488) criou **cinco PNGs candidatos** a partir do antigo `character-group-REJECTED.png`, por máscaras no mesmo canvas e sem IA:

- `guarda-esquerdo-alinhado.png` e `guarda-direito-alinhado.png`: posições derivadas do recorte original; ainda pode haver halo ou bordas incorretas.
- `kael-grupo-alinhado-REJECTED.png`: duplicata do Kael separado; não usar.
- `aldric-com-trono-REJECTED.png`: contém pixels indevidos do trono, não usar como personagem.
- `trono-halo-residual-REJECTED.png`: residual para conferência, nunca no render.

O relatório `assets/cena-01/rig-drafts/grupo/split-qa.json` registra **round-trip exato dos pixels visíveis** e classificação por peça. Isso NÃO significa que os guardas já tenham ombros, braços, mãos, cabeças e capas prontos para rig. A imagem original tem contaminação visual; a decomposição automática apenas organiza o material existente para revisão.

**Totais atuais no GitHub: 18 PNGs originais arquivados + 12 PNGs de partição de Kael + 5 PNGs de partição do grupo = 35 PNGs existentes armazenados neste canal. Nenhum deles foi desenhado de novo nesta etapa.** Oito PNGs exclusivos do chat permanecem em ZIP separado, aguardando upload ao GitHub, com SHA listado em `IMAGENS-EXTERNAS-PENDENTES.json`.


## 8. Extração fiel das duas lanças da cena-mãe, sem IA

A execução [43599262296](https://github.com/HelioConde/VideoForge-IA/actions/runs/43599262296) recortou as duas lanças **diretamente do PNG original** `assets/cenas-mae/cena-01.png`, validado pelo SHA `544548f0ac5f9e4686e2cf0d1477470f77e2fd7f15678d82799609b678fd6ebf`. O procedimento usa máscaras de polígono e linha; não chama nenhum modelo de imagem. Os arquivos estão em `assets/cena-01/rig-drafts/lancas/`:

- `lanca-guarda-esquerdo-CANDIDATE.png`: ponta superior direita, ligada à mão do guarda à esquerda, pivô provisório (381,751), caixa de conteúdo (35,321)–(816,1108).
- `lanca-guarda-direito-CANDIDATE.png`: ponta superior esquerda, ligada à mão do guarda à direita, pivô provisório (644,749), caixa de conteúdo (209,322)–(991,1106).
- `restante-cena-mae-REJECTED-AS-LAYER.png`: residual para confirmar conservação exata, **proibido como sprite móvel**.
- `split-qa.json`: recomposição dos pixels da mãe passou; isso não comprova que as máscaras não incluam fundo, luvas ou reflexos.

**Total salvo no GitHub agora: 38 PNGs**, dos quais três são recortes/residual desta etapa e oito PNGs exclusivos da conversa ainda dependem da importação binária do ZIP. As duas lanças são candidatas, **não** sprites validados para movimentar sozinhas. No plano C01-P04 os braços dos guardas precisam iniciar movimento antes das lanças, respeitando contato e hierarquia; enquanto isso não existir, render oficial bloqueado.

## 9. Inventário verificável e bloqueio editorial

O [inventário da cena 1](rig-inventario-c01.json) e [seu relatório SHA](rig-inventario-c01.qa.json) foram validados pelo [GitHub Actions 43599647856](https://github.com/HelioConde/VideoForge-IA/actions/runs/43599647856): **19 PNGs conferidos**, **16 partes candidatas/rascunho**, **1 peça rejeitada no inventário**, qualidade de rig e publicação **bloqueadas**. O enquadramento 1024×1536 para saída 1080×1920 usa fator 1,25 e corta 100px de cada lateral, sem distorção.

O arquivo [SEM-GERACAO-NOVAS-IMAGENS.lock](SEM-GERACAO-NOVAS-IMAGENS.lock) registra a instrução expressa de NÃO gerar imagens novas. Seis workflows de geração/edição do episódio já consultam esse lock e interrompem antes de chamar IA. Ele se aplica só a este vídeo, não afeta os outros canais. Só poderá ser retirado após novo pedido explícito.


## 10. Refinamento da arte original sem chamadas de IA — 56 PNGs

Em 14/11/2026, a árvore GitHub foi conferida: **56 arquivos .png** dentro de `canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/assets`. Nenhuma chamada de geração de imagens foi executada nesta etapa. O ZIP adicional com oito imagens feitas anteriormente no chat **ainda não foi importado ao GitHub**. Ele já foi validado localmente quanto a nomes e SHA, mas exige upload binário pela pasta `uploads/`.

A seleção mais recente está em [rig-selecao-artes-c01.json](rig-selecao-artes-c01.json), com SHA de cada candidato e a lista de arquivos antigos que **não podem** ser usados como base do rig.

| Subetapa | GitHub Actions | Resultado verificável | Estado artístico |
|---|---|---|---|
| Contornos dos dois guardas | [43601017320](https://github.com/HelioConde/VideoForge-IA/actions/runs/43601017320) | 4 PNGs: duas silhuetas com RGB copiado da mãe, duas versões sem lança que preservam os buracos | Pendente |
| Corrigir origem/escala de Kael | [43601362186](https://github.com/HelioConde/VideoForge-IA/actions/runs/43601362186) | Kael reposicionado ao mesmo canvas da mãe; IoU com candidato anterior ~0,278 | Pendente |
| Reaplicar máscaras anatômicas em Kael alinhado | [43601692577](https://github.com/HelioConde/VideoForge-IA/actions/runs/43601692577) | 12 partições, 11 com conteúdo, recomposição de pixels visíveis exata | Pendente |
| Isolar Aldric com contorno conservador | [43602241129](https://github.com/HelioConde/VideoForge-IA/actions/runs/43602241129) | PNG com RGB da mãe, aproximadamente 57.371 pixels de máscara; sem reconstrução de partes ocultas | Pendente |

### 10.1. Problema de escala do Kael antigo

O primeiro Kael RGBA gerado por edição foi ampliado/recomposto em escala diferente da cena original. Reutilizar suas 12 partes diretamente causaria deslocamento e duplicação. O Kael preferencial agora é `assets/cena-01/rig-drafts/kael-alinhado-original/kael-alinhado-mesma-cena-mae-CANDIDATO.png`. Suas novas peças estão em `rig-drafts/kael-alinhado-partes/`. As máscaras foram convertidas por uma transformação afim aproximada; **não são ainda separações anatômicas certificadas**.

### 10.2. Braços dos guardas, lanças e Rei Aldric

Os guardas preferenciais são `guardas-refinados/guarda-esquerdo-origem-rgb-candidato.png` e `guarda-direito-origem-rgb-candidato.png`. Os pixels RGB foram copiados da mãe, e a antiga imagem de grupo foi utilizada **somente como guia de máscara**. Cada variante `-sem-lanca-BURACOS.png` exclui trechos encobertos pela respectiva lança, identificando aproximadamente 3,6–3,7 mil pixels a recuperar com underlays antes de qualquer articulação.

Aldric agora tem `aldric-origem/aldric-RGB-da-mae-CANDIDATO.png`. O método GrabCut local tenta excluir o encosto, os braços ornamentais e os leões do trono; **o contorno ainda pode conter fragmentos do trono ou cortar tecido**. Requer inspeção humana e correção antes de montar boca/cabeça/manto.

### 10.3. Gate de produção

- Nunca substituir a pintura por uma reinterpretação do mesmo personagem, pois o recorte deve manter a mesma origem.
- O rig precisa de pivôs realmente medidos e áreas ocultas preenchidas; os candidatos atuais **não** têm esses dados.
- A comparação de reconstrução de pixels visíveis não valida movimentos articulados. Guardas e rei não podem se deslocar enquanto as mãos/ombreiras estiverem incompletas.
- Render oficial e upload YouTube continuam `false` até QA completo. O arquivo de lock continua obrigatoriamente ativo.

## 11. Auditoria de recomposição e fundo reconciliado — sem novas artes

ZIP recebido nesta conversa e conferido localmente em 14/11/2026: **8 PNGs, 8 hashes SHA-256 válidos**. O ZIP mede 8.857.833 bytes e tem SHA-256 2083cdd1425fef1b579cfb663016485a7c6b6c7279db0720db9830bd16e9b4a3. Detalhes em [qa-zip-8-imagens-existentes.json](qa-zip-8-imagens-existentes.json). **Esses oito PNGs ainda não estão no repositório GitHub:** o ZIP anexado ao chat não foi transferido pelo conector. O workflow de importação só roda após o ZIP ser enviado à pasta uploads/ do GitHub.

A primeira [QA de recomposição](qa-recomposicao-c01.json) montou sprites existentes na pose neutra apenas em memória: diferença média RGB 11,095 e 17,2064% dos pixels com erro superior a 24 em algum canal. O fundo reconstruído alterava áreas que deveriam coincidir com a cena original.

O código videoforge/reconcile_existing_background.py utilizou **somente pixels de duas imagens já existentes** para criar um candidato de fundo sem IA generativa, em assets/cena-01/candidatos/background-reconciliado-CANDIDATO.png. A operação preservou 800.935 pixels originais fora das máscaras de personagens e reduziu em 26,14% a diferença média RGB do fundo em relação à imagem-mãe.

A [segunda QA com fundo corrigido](qa-recomposicao-c01-reconciliado.json) demonstrou:

| Métrica | Original | Reconciliado |
|---|---:|---:|
| Diferença média RGB no quadro inteiro | 11,095 | 3,446 |
| Pixels com maior erro RGB acima de 24 | 17,2064% | 5,3202% |
| Diferença média na região rei/trono | 14,316 | 6,211 |
| Diferença média nas lanças cruzadas | 13,646 | 7,379 |

Os erros do quadro neutro caíram aproximadamente 69%, mas **isso não aprova animação nem garante que não surjam buracos ao movimentar personagens**. O resultado ainda é candidato e depende de revisão visual.

**Total agora verificado: 57 PNGs** armazenados no caminho do episódio em canal/alchemy-lab. A imagem nova nesta contagem é uma derivação pixel-a-pixel de duas imagens já produzidas; não houve geração de nova ilustração por IA. Os 56 PNGs anteriores foram preservados.

Próximos gates: verificar a oclusão correta das lanças e mãos; conferir Aldric sem fragmentos do trono; medir pivôs reais de Kael e guardas; avaliar em que movimentações as regiões escondidas ficam visíveis; validar composição e malhas Three.js antes de qualquer render oficial. As cenas 02 e 03 continuam reprovadas visualmente e o lock de não geração de imagens permanece ativo.

## 12. Separação de braços dos guardas e peças de Aldric (sem geração de imagens)

Esta etapa foi executada com **zero chamadas a modelos de imagem** e usando exclusivamente as cores, texturas e alfa já disponíveis no episódio. O repositório contém **71 PNGs** em `canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/assets` (57 anteriores + 8 peças de guardas + 6 peças do rei). As oito variações exclusivas do ZIP da conversa continuam fora do GitHub, aguardando envio do ZIP à pasta `uploads/`.

### C01-P04 — Dois guardas, braços independentes

- Workflow [43613024544](https://github.com/HelioConde/VideoForge-IA/actions/runs/43613024544) criou em `assets/cena-01/rig-drafts/guard-arm-parts/` **4 camadas por guarda**: corpo, braço superior, antebraço, mão segurando lança.
- As oito camadas passam na **recomposição exata** de pixels visíveis dos dois PNGs fontes, conforme `guard-arm-parts/qa.json`. Isso ainda não preenche regiões escondidas.
- A análise de contato por alfa verificou 458 pixels de sobreposição entre a mão esquerda da composição e sua lança, e 369 pixels na outra mão; o antebraço do guarda direito ainda intercepta a lança em 108 pixels.
- Foram documentados os pontos provisórios de ombro, cotovelo, punho e pega, e a hierarquia `body -> upper-arm -> forearm -> gripping-hand -> spear` em [rig-guardas-articulacoes-c01.json](rig-guardas-articulacoes-c01.json).
- O [laudo de rig](qa-guardas-articulacoes-c01.json) conferiu **10 PNGs com SHA correto** e obriga ângulos de movimento iguais a **zero** enquanto faltarem underlays, pivôs aprovados e ordenação dos planos das lanças.
- **Incompatibilidade cinematográfica:** a imagem-mãe já mostra as lanças cruzadas; a direção requer a ação de cruzá-las. Ainda faltam poses e arte original dos trechos escondidos sob mãos e antebraços. Não criar abertura artificial girando uma lança isolada ou fazendo zoom no quadro.

### Rei Aldric — seis partes reais, pose sentada

- Workflow [43613662737](https://github.com/HelioConde/VideoForge-IA/actions/runs/43613662737) executou [rig-aldric-pixel-partition.json](rig-aldric-pixel-partition.json) sem IA e salvou **6 PNGs** em `assets/cena-01/rig-drafts/aldric-partes/`.
- Peças: `coroa-cabelo-rosto`, `mao-esquerda`, `mao-direita`, `manto-esquerdo`, `manto-direito`, `corpo-vestimenta-restante`.
- Relatório `assets/cena-01/rig-drafts/aldric-partes/split-qa.json`: recomposição fiel dos pixels visíveis da fonte, sem geração ou pintura de pixels. As coroas, mãos e manto ainda não têm underlays; não há visemas nem versões de olhos abertos/fechados aprovadas.
- O candidato original de Aldric poderá conter resíduos do trono nas bordas: a divisão exata não os elimina. Não promover essas seis camadas a rig aprovado.

### Testes e proteção de recursos

- O workflow MVP foi ajustado para **não rerenderizar MP4 de teste a cada commit de PNGs, relatórios QA ou solicitações deste episódio**. Mudanças no código `videoforge/**` e testes `tests/**` continuam disparando o smoke para preservar segurança.
- Persistem: `SEM-GERACAO-NOVAS-IMAGENS.lock`, aprovação humana pendente, underlays ausentes e `video_oficial_do_programa=false`.
- **Próxima ação técnica**: revisar a silhueta de cada parte com o trono e braços; levantar máscara para oclusão correta de dedos/lanças; avaliar pose neutra e envelope máximo de movimento antes de liberar qualquer transformação do rig.

## 13. QA de movimento real do C01-P04 e trava de geração no código

Foi executada a [auditoria geométrica das articulações](qa-guardas-envelope-movimento-c01.json) no [GitHub Actions 43614298159](https://github.com/HelioConde/VideoForge-IA/actions/runs/43614298159). Ela **não gera arte**: carrega os PNGs existentes por SHA, gira somente máscaras dos antebraços+mãos em memória nos ângulos ±2°, ±8°, ±18° e mede a silhueta que fica descoberta.

| Alvo do roteiro | Guarda esquerdo (+18°) | Guarda direito (-18°) |
|---|---:|---:|
| Buracos na pose original (0°) | 0 | 0 |
| Silhueta antiga descoberta aos 2° | 286 px | 294 px |
| Silhueta antiga descoberta aos 8° | 1.094 px | 1.120 px |
| Silhueta antiga descoberta aos 18° | 2.410 px | 2.462 px |

Conclusão: os pixels reais disponíveis não bastam para rotacionar os membros sem revelar buracos. É um teste de silhueta e **não** comprova que os detalhes ocultos no uniforme, nas luvas ou no cenário estejam corretos. As lanças continuam cruzadas na arte-mãe original e não foram fingidamente descruzadas. A hierarquia em [rig-guardas-articulacoes-c01.json](rig-guardas-articulacoes-c01.json) conserva limites de rotação em 0° e `animation_or_render_allowed=false`.

### Proteção adicional contra gerar novas imagens

A proibição expressa agora existe também no Python, em `videoforge/image_generation_policy.py`, e é validada **antes da primeira chamada ao proxy** por cinco geradores: `production_art.create_image`, `production_scenes.generate_scene`, `production_scene_layers.generate`, `production_layer_recovery.recover` e `production_rgba_parts.make_part`. O bloqueio foi acrescentado também aos caminhos diretos `proxy_images.generate` e `scene_layers.generate_layer`. A proteção é específica deste episódio; outros canais mantêm seu comportamento.

Regressões em `tests/test_alchemy_no_image_generation.py` verificam que a geração para esse par canal/vídeo é negada **antes de consultar arquivos ou usar rede**. O lock do episódio segue ativo, com proteção em duas camadas (workflow e Python). Não há autorização para gerar imagens novas nem para publicar vídeos.

### Próximo trabalho antes do rig

1. Inspecionar visualmente cada junção de antebraço/luva e os pixels ocultos sob as duas hastes; os números dos testes são referência de quantos pixels ficam sem cobertura, não imagens reconstruídas.
2. Obter, a partir de materiais **já existentes e válidos**, underlays adequados. Se não houver informação visual real para recompor a anatomia oculta, manter o movimento bloqueado em vez de pintar artificialmente.
3. Resolver a diferença entre a pose inicial solicitada (lanças abertas) e a arte-mãe (lanças já cruzadas). Uma imagem nova só poderá ser gerada após autorização explícita.
4. Só com essas validações medir pivôs definitivos, verificar o plano de frente/atrás das lanças e executar os keyframes no ThreeCanvas/Remotion.

**Estado mantido:** 71 PNGs já arquivados no episódio; 8 artes externas do ZIP ainda não importadas; rig do cruzamento bloqueado; MP4 oficial de 163 segundos não renderizado.

## 14. Direção cinematográfica por plano, closes de rosto e olhos

**Pedido implementado:** alternar os enquadramentos do dorama, em vez de repetir a mesma arte de grupo/trono. A primeira imagem pode ser um establishing shot impactante, mas os planos seguintes são retratos expressivos, enquadramentos sobre o ombro, contraplano, inserts e momentos de ação com ângulo adequado.

- [Planejamento de 37 tomadas](direcao-cinematografica-planos.json) com tipo, lente, profundidade de campo, foco, emoção, elenco e frames do roteiro.
- [Guia do episódio com exemplos](GUIA-DIRECAO-CINEMATOGRAFICA.md); [guia reutilizável do projeto](../../../../docs/GUIA-ENQUADRAMENTOS-CINEMATOGRAFICOS.md).
- [QA de 36 prompts distintos](qa-direcao-cinematografica.json), sem chamar IA. Um dos 37 planos é preto absoluto, não exige PNG.
- Motor reutilizável `videoforge/cinematic_direction.py`; `production_scenes.py --shot-id C12-P01` (apenas após autorização) e campo opcional `shot_id` no workflow `production-scene-by-request.yml`.
- `C02-P01`: close do rei acusando; `C03-P01`: macro de olhos de Kael; `C12-P01`: pupilas para o lado com cabeça imóvel; `C12-P02`: over-the-shoulder revelando Elara; `C12-P03`: close de reação dela; `C14-P03`: close de Kael no cliffhanger.
- **Regra de corte:** plano geral não serve para extrair um close de rosto como resultado oficial. Precisará de uma mãe do MESMO ângulo, fundo RGBA, partes/malhas, underlays e QA; sem imagens liberadas, estes assets seguem pendentes.
- **Canonicidade visual em revisão:** os novos exemplos aprovados na conversa apresentam Kael com pano vermelho/ombreira de metal e Elara loira em vestido branco-violeta; a bíblia antiga tem roupas e cabelos distintos. O programa bloqueia novos pedidos do episódio até reconciliar essa identidade e anexar as referências reais, evitando misturar designs.
- A interface de missão é camada exclusiva do Remotion. Nada de letras ou HUD impressos no quadro. O primeiro título é elemento de montagem, não deve se repetir nas tomadas.
- **Nenhuma nova imagem foi gerada nesta etapa.** `SEM-GERACAO-NOVAS-IMAGENS.lock` permanece ativo. Não há rig final nem MP4 oficial de 163 segundos.

## 15. Timeline editorial por tomada conectada ao QA de assets

O programa agora escreve a [timeline-cinematografica.json](timeline-cinematografica.json), preparada para o compositor Remotion, com **37 tomadas contínuas, 4890 frames a 30fps e 163 segundos**, tendo corte seco entre planos (sem interpolar quadro/objeto indevidamente). A abertura `C01-P01` é preta e não precisa de PNG.

O novo módulo reutilizável `videoforge/cinematic_shot_assets.py` exige **um conjunto de assets por ângulo** para cada uma das 36 tomadas visuais, em `assets/planos/CXX-PXX/`: `scene-mother.png`, `background-reconstructed.png`, `rig.json`, `qa.json` e PNGs RGBA indicados pelo rig. O programa verifica SHA-256, tamanho 1024×1536, transparência, vinculação ao próprio plano, pivôs medidos, regiões antes ocultas, fidelidade visual, ausência de movimentação de PNG achatado e aprovação de QA.

**Situação verificada:** 1 tomada preta tecnicamente liberada; **36 tomadas visuais com imagem-mãe/rig/QA específicos pendentes**; **nenhum rig cinematográfico aprovado**. Os antigos 71 PNGs permanecem arquivados e não são apagados. Eles são candidatos e referências, mas não autorizam simular 36 ângulos novos.

O montador legado `videoforge/production_assemble.py` agora **recusa este episódio** para impedir um vídeo de 14 fotos com pan/zoom de PNG inteiro apresentado como sequência de 37 tomadas articuladas. Outros projetos sem direção cinematográfica continuam no fluxo anterior. O preflight `videoforge/official_production.py` documenta os bloqueios específicos: assets/rigs de cada plano e integração do renderer de múltiplos personagens/planos com ThreeCanvas.

O workflow [VideoForge — auditar timeline cinematográfica](https://github.com/HelioConde/VideoForge-IA/actions/workflows/qa-cinematic-edl.yml) verifica timeline, SHA, disponibilidade e bloqueios, publicando **somente JSON**. Se a timeline já existe, a reexecução aceita apenas conteúdo **idêntico**, sem sobrescrever silenciosamente alterações. A revisão de arte exige um passo próprio.

**Importante:** nenhuma nova imagem com IA, nenhum MP4 oficial de 163 segundos e nenhuma publicação no YouTube ocorreram nesta etapa. O arquivo `SEM-GERACAO-NOVAS-IMAGENS.lock` permanece ativo. Antes de futuras imagens focadas em rostos, as referências oficiais de Kael e Elara precisam ser reconciliadas com a bíblia antiga, para não trocar cabelo, roupa ou rosto entre planos.


## 16. Rig independente dos olhos — tomada C12-P01

A direção original da [tomada C12-P01](direcao-rig-remotion.json) exige, durante 120 frames (3990 a 4109, 30 fps), **cabeça e câmera rigorosamente estáticas**, enquanto as pupilas de Kael se deslocam 12 pixels no eixo X e as pálpebras acompanham 1 pixel. O programa não pode fingir esse olhar movendo o PNG inteiro.

Implementação concluída no código:
- `motion-remotion/src/eye-gaze-timeline.ts` aplica interpolação determinística, por frame local, de **0 até +12px** para as pupilas e **0 até +1px** para as pálpebras, de acordo com os keyframes do roteiro.
- `motion-remotion/src/rig-three-scene.tsx` suporta camadas transparentes independentes `pupil-left`, `pupil-right`, `eyelid-left` e `eyelid-right`. No modo exclusivo desse plano, congela corpo, cabeça e **todas as malhas do cabelo/manto** enquanto move somente essas camadas.
- `motion-remotion/src/cinematic-timeline.ts` bloqueia a renderização do plano se faltar qualquer parte ocular, se a cabeça girar, se houver piscadas genéricas, se o rosto ainda contiver as pupilas duplicadas ou se faltarem as regiões ocultas do branco dos olhos.
- `videoforge/cinematic_eye_motion.py` e `videoforge/cinematic_remotion_export.py` exigem os mesmos keyframes e aprovações no Python **antes de exportar os assets** ao Remotion.

O contrato de arte está em [rig-olhar-kael-c12-p01.json](rig-olhar-kael-c12-p01.json). Ele está explicitamente marcado como **rascunho**, não como imagem existente ou rig pronto. O [QA automatizado](qa-olhar-kael-c12-p01.json) passou em [42 testes Python](https://github.com/HelioConde/VideoForge-IA/actions/runs/43641372475) e [9 testes Node + TypeScript](https://github.com/HelioConde/VideoForge-IA/actions/runs/43641389882).

**Bloqueios que permanecem:** falta a própria imagem-mãe do close, as quatro partes RGBA recortadas da mesma arte, preenchimento comprovado da esclerótica atrás das pupilas, QA da máscara sem vazamento e aprovação visual. Portanto nenhum MP4 oficial foi renderizado e nenhum PNG novo gerado. O lock `SEM-GERACAO-NOVAS-IMAGENS.lock` permanece ativo.


## 17. Auditoria de transparência das pupilas e esclerótica (C12-P01)

O código passou a medir **a silhueta real de todos os pixels de alfa maior ou igual a 1**, incluindo franjas semitransparentes, no deslocamento de pupilas e pálpebras do close de Kael. Essa validação não é apenas uma flag de `qa.json`: ela precisa abrir os arquivos PNG originais por SHA-256, aplicar os deslocamentos em memória e verificar a cobertura da esclerótica/rosto.

O módulo `videoforge/cinematic_eye_pixel_audit.py` exige:

- Quatro peças oculares RGBA separadas (`pupil-left/right` e `eyelid-left/right`), mais `head-open` da mesma imagem-mãe `C12-P01`.
- Duas máscaras de segurança de esclerótica, esquerda e direita, com proveniência por SHA da mesma arte.
- Teste de **30 deslocamentos inteiros**: pupilas de 0 a 12px, pálpebras de 0 a 1px, ambas para cada olho.
- Zero pixel da pupila/pálpebra ultrapassando a região segura, zero recorte na borda do canvas e zero pixel sem cobertura do rosto.
- Esclerótica e underlay da cabeça com **alfa mínimo de 254** nas regiões alcançadas; detectar inclusive franjas com alfa **1**.
- Aprovação visual **independente** para cor natural do branco dos olhos, ausência de pupila duplicada na pintura do rosto e máscaras do enquadramento.

Os resultados automáticos de máscara **não comprovam sozinhos que a cor/anatomia está correta**, portanto nenhuma aprovação humana é inferida. O código que envia material ao Remotion executa essa auditoria novamente, para impedir falsos positivos por JSON alterado.

O workflow [QA de pixels dos olhos C12-P01](https://github.com/HelioConde/VideoForge-IA/actions/runs/43642952433) executou **17 testes com sucesso**, sem criar PNGs; o relatório [qa-pixel-olhos-c12-p01.json](qa-pixel-olhos-c12-p01.json) registra o estado **`awaiting_own_shot_art`**, com bloqueios para `assets/planos/C12-P01/rig.json` e `qa.json`, ainda ausentes.

Quando os arquivos forem anexados à pasta `assets/planos/C12-P01/`, o workflow `.github/workflows/qa-alchemy-eye-pixels.yml` será disparado automaticamente para reavaliar os pixels. **Não há geração de imagens**, reinterpretação artificial de rosto nem MP4 nesta tarefa.

Uma incompatibilidade de testes foi encontrada e corrigida: o workflow MVP legado não instala Pillow, então os novos testes oculares agora se comportam como os testes de recorte existentes — são ignorados naquele ambiente e **obrigatórios nos workflows específicos que instalam Pillow**. O projeto mantém o pipeline antigo separado do QA cinematográfico.

## 18. Continuidade entre os 37 ângulos e segurança subpixel

A auditoria ocular agora considera também a filtragem **subpixel** do Remotion/Three.js. Um deslocamento de pupila de 4,5 px pode revelar um halo mesmo que os testes em 4 e 5 px não revelem falhas; para isso, `videoforge/cinematic_eye_pixel_audit.py` amplia conservadoramente a silhueta alfa em 1 px (filtro 3×3), exigindo cobertura da esclerótica em todas as bordas e antialias. A técnica não muda os PNGs e não cria imagens. Os testes incluem furo no underlay invisível nos deslocamentos inteiros, mas revelado no bilinear.

Também foi criado [qa-inventario-tomadas-cinema.json](qa-inventario-tomadas-cinema.json), com SHA-256 de **14 imagens-mãe arquivadas**, mapeamento de referências para as **37 tomadas** e prioridade de elaboração dos **12 closes de rosto/olhos**. As **52 imagens rascunho da C01** permanecem separadas das 14 mães de referência. Essa catalogação **não** equivale a gerar nem aprovar uma imagem-mãe própria de cada plano. O total de PNGs arquivados no episódio continua **71**.

O [GitHub Actions de QA](https://github.com/HelioConde/VideoForge-IA/actions/runs/43643929373) concluiu com **59 testes Python aprovados**. A timeline original de 4890 frames permaneceu intocada; nenhuma nova imagem foi gerada. O inventário registra que os **36 planos visuais ainda não têm artes e rigs específicos aprovados**, e as imagens aprovadas no chat seguem pendentes de integração ao repositório.

**Apresentação ao usuário:** durante revisões visuais deste dorama, mostrar as imagens disponíveis diretamente na conversa, indicando sua condição (referência, rascunho, aprovada ou rejeitada), além de manter o arquivo original e o histórico dentro de `canal/alchemy-lab`. Não afirmar que a visualização no chat importou uma imagem ao GitHub.


## 19. Canvas nativo por plano — preservar os closes v2 sem cortar rosto

**Correção do render:** as referências de Kael e Elara aprovadas como estilo estão em **941×1672 pixels RGB**, muito próximas de 9:16. As 14 imagens-mãe históricas do episódio estão em **1024×1536 (2:3)**. O programa não deve exigir que uma foto 941×1672 seja redimensionada/esticada para 1024×1536.

Os módulos \`videoforge/cinematic_shot_assets.py\`, \`videoforge/cinematic_remotion_export.py\` e \`videoforge/cinematic_eye_pixel_audit.py\` agora aceitam, após declaração e aprovação por tomada, **uma destas duas dimensões nativas**:

- \`{"canvas":{"width":941,"height":1672}}\` — closes/referências cinematográficas em quase 9:16.
- \`{"canvas":{"width":1024,"height":1536}}\` — cenas-mãe legadas 2:3.

Mãe, fundo reconstruído, recortes de partes e rig do MESMO plano precisam ter dimensões e \`bbox\` coerentes, hashes SHA-256 e QA visual. O Remotion recebe \`sourceCanvas\` por shot e recusa divergências. A matemática de \`cover\` do canvas e do background usa escala **uniforme**, sem esticar e deformar a face.

**Comparação objetiva para saída 1080×1920 (9:16):**
- Original **941×1672** → corte horizontal de **0,25 pixel em cada lado** da arte original; praticamente a imagem inteira permanece visível.
- Original **1024×1536** → corte horizontal de **80 pixels de cada lado** da arte original no enquadramento vertical.

Para todo plano \`close_up\`, \`extreme_close_up\` ou \`insert\`, o arquivo \`qa.json\` precisa informar \`focal_bbox:[x,y,largura,altura]\`, medido **na mãe original** e centrado nos olhos, expressão ou objeto focal. \`videoforge/cinematic_frame_fit.py\` verifica que essa região continua 100% visível após \`cover\`, respeitando margem de segurança de 2px; o TypeScript do Remotion repete a verificação antes de montar o vídeo. Cortar cabelo/ombro deliberadamente em um close pode ser correto, mas **cortar olhos e objeto focal por erro de proporção é bloqueado**.

Os testes foram executados com sucesso: [65 testes Python](https://github.com/HelioConde/VideoForge-IA/actions/runs/43646668407) e [TypeScript/Remotion](https://github.com/HelioConde/VideoForge-IA/actions/runs/43646674144). Estas são **verificações geométricas**, não aprovação das imagens-mãe, fundos/underlays ou 36 rigs ausentes.

O episódio permanece com \`SEM-GERACAO-NOVAS-IMAGENS.lock\` ativo; os arquivos históricos seguem intactos. O MP4 oficial continua bloqueado por falta de arte e rig próprios de cada um dos 36 planos visuais. As imagens de referência exibidas no chat não podem ser tratadas como PNGs já importados no GitHub.


## 20. Primeiro MP4 de aprovação produzido — C12 (12 segundos)

**Resultado real de 14/11/2026:** foi renderizado um MP4 de 12 segundos a partir dos três PNGs originais disponíveis na conversa, com composição em memória e sem gerar novos PNGs. O arquivo está disponível na própria conversa para aprovação, **não** no GitHub/YouTube.

- Arquivo: alchemy_c12_primeiro_mp4_aprovacao.mp4
- SHA-256: 22417e6023f90a8c68d48b21c3a28903f719c63f5290b7152821f9f7b67d5a58
- Formato: 720×1280, 30 FPS, 360 quadros, 12 segundos, H.264 + AAC; 975443 bytes.
- C12-P01 (0–4s): close de Kael, fonte olhar_tenso_no_salão_real.png, pequenas camadas de pupila alpha independentes.
- C12-P02 (4–8s): plano OTS Kael/Elara/Aldric, fonte confronto_no_trono_real.png, efeitos de ambiente separados.
- C12-P03 (8–12s): reação de Elara, fonte princesa_intrigada_no_trono_real.png, pequenos movimentos de pupila e pensamento original do roteiro.
- Áudio: atmosfera e nota de reconhecimento sintetizadas especialmente para a cena, sem música comercial.

**Escopo:** este arquivo é um **animatic para aprovação visual**, não animação 2D definitiva por malha. Cabelo, capa, vestes, braços, underlays e rigs não estão aprovados. Os pixels dos três PNGs fontes não foram modificados. Este preview não valida automaticamente os 36 planos visuais nem libera o MP4 oficial de 163s.

Ver [qa-primeiro-mp4-c12.json](qa-primeiro-mp4-c12.json) para hashes, duração e fontes. Ainda é necessário importar os bytes do vídeo e dos PNGs para o GitHub e obter revisão do usuário. O lock SEM-GERACAO-NOVAS-IMAGENS.lock continua ativo; não fazer upload ao YouTube.


## 21. Prévia C12 v2 — deformação real de malha em partes independentes

**Correção da objeção do usuário:** a prévia C12 v1 era apenas um animatic de olhos e partículas. A nova prévia C12 v2 contém **cinco camadas RGBA derivadas dos três PNGs originais**, com **512 triângulos** deformados independentemente, sem mover o PNG inteiro: uma dobra da capa de Kael em C12-P02 e duas mechas, um brinco pivotado e um trecho do tecido de Elara em C12-P03. O plano C12-P01 continua de **olhar independente, sem movimentar cabeça, cabelo ou capa**.

- Vídeo local de 12 s e 360 frames: `alchemy_c12_mesh_rig_v2_aprovacao.mp4`, 720x1280 H.264/AAC, SHA-256 `e08f79924e6f09bab195e54d49c32b588c2438d28faf2e1db12d626bba018016`.
- [Contrato das cinco malhas](qa-c12-rig-malha-v2.json). A origem é 941x1672, e cada recorte tem pivô, amplitude, malha e posição medida na arte original.
- Pacote técnico dos recortes: `alchemy_c12_rig_camadas_tecnicas_v2.zip`, disponível **como anexo na conversa**, com cinco PNGs RGBA e dois fundos de recomposição derivados das artes originais. **Não foi enviado ao GitHub.**
- QA de recomposição em resolução nativa (média de diferença absoluta em nível de cor): C12-P02 **0,0009** e C12-P03 **0,0069**. Existem alguns pixels de borda ainda acima do limite visual, principalmente nos recortes do cabelo e do brinco. **Ainda não aprovados.**
- A prova local utilizou rasterização determinística de malhas triangulares para obter um MP4 real de teste. O **pipeline de produção continua sendo Remotion + ThreeCanvas**. A atualização de `motion-remotion/src/rig-three-math.ts` permite brinco por pivô de osso, e `motion-remotion/src/c12-mesh-technical.tsx` fornece compositor Three.js **isolado, apenas técnico**, que exige os PNGs originais previamente importados e hashes específicos.
- Testes de segurança impedem que a prévia técnica marque os 36 planos ou rigs oficiais como aprovados, e que passe SHA/bbox de outra câmera.

**Limitações ainda abertas, sem atalhos:** não temos todos os elementos da anatomia articuláveis da cabeça, braços, ombros, cabelo inteiro e manto. O segmento do brinco ainda inclui pixels adjacentes na máscara; as regiões ocultas precisam de QA visual. O close C12-P01 ainda necessita da execução final do deslocamento ocular de 12 px em sprites de pupila/esclerótica separados e aprovados. O MP4 v2 demonstra malha verdadeira **parcial**, mas ainda não é o rig **completo** requerido para uma cena oficial. Os PNGs de origem e o MP4 não estão no repositório; lá existem atualmente apenas metadados, componentes e testes. Não publicar no YouTube, não desativar o lock de geração de novas ilustrações.
