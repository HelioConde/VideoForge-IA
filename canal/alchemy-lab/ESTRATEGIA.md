# Estratégia editorial — Alchemy Lab (dorama experimental)

> **Plano editorial, não execução.** Pesquisa de trends, vidIQ, geração de imagens, narração, Analytics e publicação são integrações futuras. Não criar candidatos, reservas, históricos ou métricas fictícios. Ler antes: `README.md`, `AGENTS.md`, `docs/ARQUITETURA.md`, `docs/REGRAS-EDITORIAIS.md`, `docs/ESTRATEGIA_SHORTS.md`, `canal/README.md`, `canal/<id>/README.md` e histórico **do próprio canal**.

## Posicionamento e meta

Canal em **modo de laboratório editorial**, com foco inicial em **doramas**, especialmente histórias dramáticas e românticas que possam ser contadas com ilustrações originais de IA. A natureza de teste permite comparar gêneros, mas não significa publicar conteúdos aleatórios sem coerência. Testar blocos editoriais identificáveis antes de decidir se o canal deve se especializar em um formato.

- **Público:** espectadores brasileiros interessados em romances, relações complexas, suspense e reviravoltas no estilo dorama; idioma pt-BR.
- **Promessa editorial:** pequenos dramas com protagonistas próprios, emoção e resolução, sem fingir que uma história original é uma cena real de série existente.
- **Formato:** narrador + cenas originais geradas por IA + legendas. Não usar cenas ou OST de dramas de terceiros sem direitos/licença.
- **Hipóteses iniciais de teste (não proporções validadas):** 50% mini-doramas românticos originais, 25% dilemas/reviravoltas, 15% suspense/mistério leve, 10% análise de clichês/tropes de doramas em alta.

## Radar de tendências específico

Pesquisar termos em português e variantes coreanas traduzidas: “dorama em alta”, “k-drama romance”, “final explicado”, “dorama vingança”, “doramas de 2026”, “triângulo amoroso”, etc. Confrontar YouTube Search/Shorts por período, [Google Trends](https://trends.google.com/trends/), [Top 10 Netflix de séries não inglesas](https://www.netflix.com/tudum/top10/pt-br/tv-non-english) **filtrando realmente as produções do gênero**, anúncios oficiais de plataformas e comentários públicos pertinentes. O Top 10 geral não prova que um item é dorama nem que esse tema está popular entre espectadores do canal.

**Como usar a tendência:** se uma obra real em alta tiver trope relevante (ex.: amor proibido, troca de identidade), escrever um **enredo novo com personagens novos**, não recapitular episódios nem imitar o elenco. Alternativamente, fazer comentário editorial sobre o trope, com fatos checados.

## Formatos e exemplos de testes (não são tendências medidas)

- Micro-história: “Ela recebeu uma carta destinada ao seu futuro marido…” com começo, conflito e desfecho próprios.
- Suspense romântico: “O noivo desapareceu no dia do casamento — mas deixou uma chave”.
- Reviravolta de relacionamento: “Ele descobriu quem salvou sua família anos atrás”.
- Explicação de tema: “Por que o trope de identidade secreta prende tanto nos doramas?” com análise própria.

Evitar episódios intercambiáveis com apenas nomes e roupas trocados; variar conflito, estrutura, personagens e resolução. Sinalizar claramente quando for **ficção original** e não reportagem/recap.

## Arte, áudio e direção

Definir estética cinematográfica ilustrada ou 2.5D **para o vídeo todo**: personagens originais com ficha de rosto/roupa/idade, cenários (café, escola, cidade etc.) e paleta constantes. A IA deve expressar emoção com enquadramentos e composição, não com repetição do mesmo retrato. Evitar usar rosto/voz de atores reais, pôsteres oficiais, marcas e cenas de séries sem autorização. Música original ou licenciada compatível com drama.

## Pontuação de pauta (0–5 por critério)

Demanda de busca/tendência verificável **20%**; identificação emocional e clareza do conflito **20%**; capacidade de contar apenas com imagens de IA **20%**; ângulo realmente original **20%**; gancho e desfecho **10%**; direitos/segurança **10%**. Direitos e veracidade são vetos antes da pontuação.

## Experimento e aprendizado

Comparar blocos de gênero em uma janela editorial sugerida de quatro semanas **somente quando houver capacidade de publicação e dados reais**. Observar espectadores que escolhem assistir, retenção, percentual médio assistido, visualizações engajadas, inscritos por mil visualizações engajadas e comentários quando disponíveis. Se um formato tiver melhor desempenho, aprofundar **sem repetir o mesmo enredo**. Não alterar nicho com base em um único viral.

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

**Origem e limite dos dados:** o relatório de pesquisa aprofundada, baseado nas exportações do YouTube Studio de **16/10 a 13/11/2026**, apresenta **179 visualizações** e **0 inscritos ganhos**. **Os dados analisados ainda refletem conteúdos anteriores de tecnologia**; portanto, **não medem** a aceitação do novo posicionamento de microdoramas. Estes números não foram revalidados diretamente nos CSVs nesta atualização.

**Hipótese editorial:** testar **microdoramas de ficção original** com conflito identificável nos primeiros 1–3 segundos, progressão emocional, virada narrativa e desfecho coerente. Evitar imitar roteiros, atores, cenas ou OST de doramas existentes. Não declarar que o novo nicho falhou ou funcionou antes de publicar e medir vídeos reais desse formato.

**Plano experimental de 30 dias:** até **10 candidatos** — 4 romances originais, 3 dilemas/reviravoltas, 2 suspenses leves e 1 análise original de trope. Esta distribuição é **proposta de organização**, não transcrição das dez ideias do relatório. Cada história deve ter protagonistas, premissa e resolução realmente distintos; não produzir histórias em massa que só troquem nomes.

**Aprendizado:** registrar em cada teste o conflito inicial, estrutura, duração, estilo de arte e desfecho. Com acesso autorizado a dados **deste canal**, comparar escolha de assistir, visualizações engajadas, duração/percentual assistido, inscritos e comentários elegíveis. Distinguir claramente resultados de vídeos antigos de tecnologia e novos microdoramas; a amostra inicial pode ser insuficiente.

**Portões antes de produzir:** personagens originais e consistentes, música/voz com direitos, cenas que sustentem a história e revisão humana. O gerador de doramas ainda não existe como sistema operacional; o plano não autoriza IA paga, upload nem novos agentes.
