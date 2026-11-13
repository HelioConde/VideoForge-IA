# Estratégia editorial — Otaku Multicena (Otaku BR)

> **Plano editorial, não execução.** Pesquisa de trends, vidIQ, geração de imagens, narração, Analytics e publicação são integrações futuras. Não criar candidatos, reservas, históricos ou métricas fictícios. Ler antes: `README.md`, `AGENTS.md`, `docs/ARQUITETURA.md`, `docs/REGRAS-EDITORIAIS.md`, `docs/ESTRATEGIA_SHORTS.md`, `canal/README.md`, `canal/<id>/README.md` e histórico **do próprio canal**.

## Posicionamento e meta

**Canal de anime para público brasileiro em português**, com explicações, curiosidades, análises e teorias originais sobre animes que despertem interesse comprovado. Produção planejada com ilustrações de IA e narração; **sem depender de clipes, episódios, OST ou imagens oficiais de anime**.

- **Pilares iniciais para testar:** 35% curiosidades e fatos de personagens/obra, 25% explicações de poderes e acontecimentos, 25% teorias e cenários hipotéticos claramente identificados, 15% lançamentos e assuntos em alta com fontes oficiais.
- **Regra de programação:** uma hipótese editorial por vídeo, com contexto para fãs novos e profundidade para fãs recorrentes. Evitar títulos que entreguem spoilers involuntariamente; sinalizar spoilers quando necessário.
- **Pausa editorial atual:** evitar novas pautas de **Death Note** até orientação contrária do usuário, pois já houve excesso dessa franquia na programação anterior. Pesquisar outras obras e perspectivas. Isso não implica apagar vídeos existentes.

## Radar de tendências específico

Cruzar YouTube Search/Shorts Brasil, Google Trends em pesquisa do YouTube e região Brasil, anúncios e calendários oficiais de distribuidoras/estúdios, páginas de séries licenciadas (ex.: [Crunchyroll News](https://www.crunchyroll.com/news)), discussões públicas e, quando autorizado, vidIQ e Analytics do próprio canal. Distinguir anúncios oficiais de rumor, meme e teoria de fã. Comparar interesse recente (ex.: 7/30 dias) e pertinência ao público; não inferir que anime popular na comunidade é automaticamente tema novo no canal.

## Ideias de formatos (templates não verificados)

- “O detalhe que explica a decisão de [personagem] em [anime]” — citar arco/episódio/fontes.
- “Como funciona a habilidade de [personagem]?” — diferenciar funcionamento canônico e interpretação.
- “E se [acontecimento] tivesse sido diferente?” — hipótese declarada, roteiro criativo e independente.
- “O que mudou no anúncio de [temporada]?” — somente após confirmação pública oficial.

## Técnica de imagens IA e direitos

Criar **bíblia visual** do episódio: anime ilustrativo coerente, paleta, proporções, figurino, poses, locais, acessórios e traços fixos em todas as cenas. **Não alternar anime, fotorrealismo e novos desenhos em cada imagem**, nem mudar o rosto/cabelo do mesmo personagem. Toda ilustração precisa acompanhar a narração, com cortes e progressão visual. Evitar reproduzir screenshots, key visuals, pôsteres ou personagens protegidos sem verificar os direitos; originalidade editorial e arte original não eliminam automaticamente questões de propriedade intelectual de uma franquia. Não usar OST original sem licença.

**Piloto técnico:** manter 90–180 segundos, 9:16 e QA do `README.md`. O MVP só renderiza imagens/áudio fornecidos; gerador IA e animação por camadas **não estão implementados**. Shorts acima de um minuto com reivindicação ativa de copyright podem ser bloqueados globalmente.

## Pontuação de pauta (0–5 por critério)

Demanda atual verificada **25%**; afinidade com público deste canal **20%**; novidade diante do histórico (incluindo Death Note) **20%**; viabilidade artística/visual com IA **15%**; precisão e fontes **10%**; força narrativa **10%**. Direitos, repetição ou fatos sem fonte são vetos.

## Avaliação e melhoria

Observar por obra, categoria de tema e formato a decisão de assistir/deslizar, retenção, percentual visualizado, visualizações engajadas, inscritos gerados e busca quando Analytics estiver autorizado. Testar gancho direto vs pergunta e curiosidade vs explicação de consequência, **sem repetir assunto ou vídeo**. Preferir aprofundar novos ângulos com fatos e contribuição substancial.

## Execução editorial e rastreabilidade (a implementar)

1. Conferir identidade, idioma, histórico e reservas **deste canal** e inventário real do YouTube quando conectado; índice vazio não prova ausência de vídeos.
2. Pesquisar várias ideias atuais com links e datas. Não chamar qualquer título de “em alta” sem evidências verificáveis.
3. Eliminar assuntos repetidos, histórias quase iguais, dados sem fonte, risco de direitos ou impossibilidade de representar o tema com imagens de IA.
4. Atribuir notas editoriais justificadas (0–5 em cada critério ponderado); as notas são **avaliação interna**, jamais números de Analytics ou “score do algoritmo”. Quando faltar evidência, marcar como pendente, sem simular resultados.
5. Registrar candidato realmente pesquisado em `editorial/pesquisas/YYYY-MM-DD.json` e, após seleção real, em `editorial/candidatos.json` / `reservas.json`. Usar `videos/<video-id>/editorial.json` para roteiro, palavras-chave, fontes, guia visual, direitos e aprovação; `video.json` continua exclusivamente técnico.
6. Criar roteiro com gancho imediato, progressão, desfecho e indicação de cada cena; produzir uma **bíblia visual** única por vídeo antes das imagens (estilo, personagens, roupa, cenário, cor, proporções, luz). Usar a mesma base de referência nas cenas, revisar consistência e corrigir imagens discrepantes. Imagens devem ser pertinentes ao que é narrado, não um slideshow genérico.
7. Fazer QA editorial (originalidade, idade, precisão, direitos, legibilidade, coerência visual), além de QA técnico do MP4. Não afirmar produção, upload ou desempenho sem artefatos reais.
8. Quando houver publicação autorizada, acompanhar resultados por vídeo no histórico do **mesmo canal** e revisar temas, ganchos, formatos e frequência a partir dos dados reais; não há garantia de viralização nem obrigação de postar diariamente.

**Fontes transversais:** [YouTube Creators](https://www.youtube.com/intl/pt-BR/creators/), [descoberta de Shorts](https://support.google.com/youtube/answer/11914225?co=YOUTUBE._YTVideoType%3Dshorts&hl=pt-BR), [até 3 minutos e copyright](https://support.google.com/youtube/answer/15424877?hl=pt-BR) e [conteúdo inautêntico](https://support.google.com/youtube/answer/1311392?hl=pt-BR). Temas e fontes sugeridos abaixo são **pistas para pesquisa**, não resultados atuais já verificados.

## Ciclo experimental de Shorts — diagnóstico de 13/11/2026

**Origem e limite dos dados:** o relatório de pesquisa aprofundada, elaborado a partir de exportações do YouTube Studio de **16/10 a 13/11/2026**, informa **12.774 visualizações**, **+41 inscritos** e **33,96% que continuaram assistindo** no agregado analisado. Estes valores são **transcrição do diagnóstico relatado**, não uma nova leitura independente dos CSVs nem uma conexão ativa com Analytics. A taxa de quem continuou assistindo mede a decisão de ver em vez de deslizar; **não** é sinônimo de retenção média.

**Diagnóstico editorial:** já existe alcance relevante; a hipótese prioritária é melhorar a clareza e o interesse do **gancho nos primeiros 1–3 segundos**, sem sacrificar explicação, precisão ou conclusão. Investigar obras com demanda demonstrável em vez de aumentar volume indiscriminadamente. **Death Note continua pausado** para novas pautas, até instrução explícita em contrário.

**Plano sugerido para os próximos 30 dias (não é fila de produção):** até **10 Shorts candidatos**, distribuídos como hipótese de teste em 4 curiosidades de obras distintas, 3 explicações de poderes/regras, 2 análises ou teorias originais claramente sinalizadas e 1 anúncio confirmado. Esta distribuição é **proposta operacional**, não reprodução das dez ideias detalhadas do relatório; escolher cada tema só depois de inventariar o canal, conferir fontes, direitos e reservas. O piloto técnico continua exigindo **90–180 segundos**.

**Teste prioritário:** contrastar abertura com consequência concreta versus pergunta específica, usando pautas diferentes e anotando que diferenças de tema também afetam os resultados. Acompanhar, apenas com dados autorizados deste canal, **continuaram assistindo versus deslizaram**, visualizações engajadas, duração/percentual médios, retenção por trecho e inscritos. Rever a hipótese após um conjunto suficiente de publicações; não atribuir causalidade a uma amostra pequena.

**Portões antes de qualquer produção:** histórico real e repetição, checagem de canon/teoria, spoilers, licença de arte/áudio, bíblia visual consistente e revisão editorial. Não atualizar `candidatos.json`, `reservas.json` ou `historico-videos.json` como se os dez vídeos já existissem.
