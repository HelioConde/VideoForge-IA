# Estratégia de YouTube Shorts — VideoForge IA

> Atualizado em 2026-11-13. Guia editorial **para futuras integrações**. A existência deste documento não significa que pesquisa, agentes, geração por IA, YouTube Analytics ou publicação automática já estejam implementados.

## Ordem obrigatória de leitura

Leia README.md, AGENTS.md, docs/ARQUITETURA.md e **este guia** antes de propor pesquisas ou roteiros de Shorts. Depois leia canal/<id>/canal.json, canal/<id>/README.md, canal/<id>/conteudos/indice.json e os registros editoriais **do mesmo canal**. Não tratar dados de outros canais como histórico do canal atual.

## Objetivo

Produzir Shorts originais e coerentes com o público de cada canal, com foco em satisfação, retenção e crescimento sustentável. Volume, hashtags, músicas populares, horários e promessas de “viralização” **não garantem entrega**. Os sinais oficiais incluem: decisão de assistir versus ignorar, duração média da visualização, percentual médio assistido, curtidas e pesquisas de satisfação. Consultar documentação oficial antes de mudar regras.

## 1. Pesquisa ANTES de escolher o assunto

1. Entender a identidade, idioma, público-alvo e histórico do canal; **não misturar os cinco canais**.
2. Com autorização e integração real, analisar vídeos **do próprio canal**: visualizações engajadas, visualizações, escolha de assistir/deslizar, duração média, percentual médio assistido, inscritos adquiridos, fontes de tráfego e comentários quando disponíveis.
3. Procurar temas relevantes: YouTube Search/Autocomplete, Google Trends configurado para Pesquisa no YouTube, tendências de nicho, vidIQ/alternativas quando autorizadas, concorrentes e perguntas de espectadores.
4. Verificar data, fonte, tema, tendência crescente/decrescente, concorrência e adequação à audiência. Dados sobre concorrentes são apenas públicos; dados privados próprios exigem OAuth/autorização. Nunca inventar números de pesquisa, CTR, retenção ou volume.
5. Propor **ângulo original**, com hipótese de interesse e uma promessa que o roteiro possa cumprir. Inspirar-se em temas não é copiar vídeos, roteiros, imagens ou áudio.
6. Antes de reservar pauta, comparar assunto, personagens, anime/jogo, perspectiva, palavras-chave e enredo contra indice, candidatos, reservas e vídeos **do mesmo canal**; vetar conteúdo igual ou muito parecido. Registros vazios não provam que vídeos antigos não existem.

Guarde resultados verificáveis em canal/<id>/editorial/pesquisas/YYYY-MM-DD.json **apenas quando a pesquisa efetivamente ocorrer**, com fonte, horário da consulta e dados observados. Candidatos e reservas só podem ser atualizados após decisões reais. Este documento não é uma fila automática.

## 2. Estrutura editorial de um Short

- **Primeiros 1–3 segundos**: começar com o fato, conflito, imagem relevante ou pergunta específica, sem vinheta demorada nem pedido de inscrição.
- **Corpo**: uma ideia central, contexto suficiente, progressão clara (pergunta/obstáculo → desenvolvimento → descoberta/solução) e valor real ao espectador.
- **Ritmo visual**: alternar enquadramento, movimento, legendas e cenas **quando ajudar a compreensão**. “Mudar a cada cinco segundos” é hipótese de teste, não regra do YouTube.
- **Final**: cumprir a promessa, dar encerramento satisfatório e só usar CTA breve quando relevante; jamais enrolar ou fazer promessa enganosa para prolongar visualização.
- **Consistência artística obrigatória**: mesma direção de arte, aparência dos personagens, cenários e continuidade temporal em todas as cenas de um vídeo. Não alternar aleatoriamente desenho/anime e realismo. Revisão visual é separada do QA técnico.
- **Acessibilidade**: fala clara e áudio inteligível, legendas sincronizadas e textos legíveis sem cobrir o foco da imagem.
- **Originalidade**: evitar estruturas quase idênticas com simples substituição de nomes, narração genérica repetida, slideshow indistinguível ou reaproveitamento sem contribuição substantiva.

## 3. Duração e formato

- A regra oficial atual permite **Shorts quadrados ou verticais de até 3 minutos** (para uploads regulares desde 2024-10-15).
- Para o piloto Otaku Multicena deste repositório, **preservar 90–180 segundos**, 9:16, 1080×1920, H.264/AAC e QA; duração menor só com alteração explícita dos requisitos do projeto.
- Não aplicar automaticamente a recomendação “15–30 segundos”: muitos materiais fornecidos citam o limite antigo de 60 segundos. A duração ideal depende da narrativa e dos dados de cada canal.
- Shorts com **mais de 1 minuto** e reivindicação de direitos autorais ativa de qualquer tipo são bloqueados globalmente. Preferir mídia original/licenciada e conferir direitos de imagem, música e vídeo. Não presumir que áudio “em alta” pode ser usado fora das condições da plataforma.

## 4. SEO e descoberta

- Título fiel ao conteúdo, natural, específico, com termo pesquisado quando fizer sentido; não clickbait enganoso.
- Descrição curta contextualizando assunto e fontes; hashtags **poucas e relevantes**, sem enchimento. Tags/hashtags não substituem retenção nem satisfação.
- Capa/frame legível e visualmente fiel ao conteúdo quando aparecer em busca/perfil; sem afirmar que thumb controla a distribuição do feed.
- Sons em alta podem ajudar a encontrar audiência relevante **apenas se licenciados e adequados**; não são garantia de recomendação.
- Avaliar a possibilidade de associar um vídeo relacionado e de direcionar para séries ou conteúdos longos, sem presumir conversão automática.
- Comentários: responder quando adequado; comentário fixado/CTA só quando o recurso está disponível e compatível com as configurações do vídeo. Para conteúdo **feito para crianças**, não planejar estratégias que dependam de comentários.

## 5. Medição e testes

Medições **somente após acesso autorizado** e existência de dados. Para cada vídeo, registrar data, canal, formato, duração e tema antes de comparar resultados.

Priorizar na revisão: 
1. Exibições no feed, escolha de assistir versus deslizar (gancho).
2. Duração média da visualização e percentual médio assistido (corpo/ritmo).
3. **Visualizações engajadas**, distintas das visualizações simples.
4. Sinais de satisfação (curtidas, feedback) e inscritos adquiridos por mil visualizações engajadas, quando o denominador existir.
5. Origem de tráfego, pesquisa, comentários elegíveis, retenção por trecho e comparação de desempenho entre vídeos do **mesmo canal**.

Desde **2025-03-31**, visualizações simples de Shorts contam início/replay sem tempo mínimo; elegibilidade e receita de Shorts usam **visualizações engajadas**. Não comparar números pré/pós mudança como se a definição fosse idêntica.

Testes controlados sugeridos (hipóteses internas, não certezas algorítmicas): abertura direta vs pergunta; variações de ritmo; miniatura/frame; título curioso vs informativo; duração **dentro dos limites vigentes do canal**; formatos narrativos; horários inferidos pela atividade da audiência. Variar uma dimensão por vez, registrar amostra e evitar conclusões com poucos dados. Revisar o desempenho após publicação, mas não prometer viralização.

## 6. Regras para agentes futuros e proteção

- O **responsável editorial do canal** pesquisa e decide com evidências; futuras funções de roteiro, SEO, arte, narração e QA recebem um briefing rastreável. Nenhuma dessas funções é declarada operacional enquanto não houver código, integração e testes.
- Sem repetir tema/enredo/abordagem quase idêntica no canal; pesquisa de concorrente não autoriza cópia.
- O supervisor editorial deve barrar roteiro não verificado, conteúdo sem originalidade, inconsistência visual, arquivos sem direito de uso e decisões baseadas em métricas inventadas.
- Conteúdo produzido em massa, repetitivo ou com diferenças apenas superficiais pode ser classificado como **inautêntico** para monetização. Uso de IA por si só não é proibido; o resultado precisa de contribuição substantiva.
- Se conteúdo gerado/alterado por IA for realista de modo que possa confundir o público, aplicar a divulgação de conteúdo sintético conforme a regra oficial. Animações claramente fantasiosas não exigem automaticamente a mesma divulgação.
- Sem gastos com APIs, uso de segredos, upload público ou privado e nem execução automática sem a autorização correspondente. Não enfraquecer QA fail-closed existente.
- Para novas implementações: primeiro testes offline e review em PR; não confundir documentação com sistema funcionando.

## 7. Materiais fornecidos em 2026-11-13

**Síntese editorial**, não cópia integral dos artigos. O material abaixo serviu como insumo, não como garantia sobre o algoritmo:
- “4 Dicas para Crescer seu Canal com Shorts do YouTube” — texto compartilhado: SEO, tendências, respostas e comentários fixados.
- “10 Dicas para fazer Shorts viralizarem no YouTube” — artigo sobre ganchos, temas, ritmo e publicação; contém referência antiga a 60 segundos.
- “Como encontrar e usar as tendências de pesquisa do YouTube para impulsionar seu canal” — Semrush (2024): Google Trends, pesquisa, concorrência, palavras-chave.
- “18 Dicas para Fazer seus Vídeos do YouTube Shorts Bombar” — AIR Media-Tech (atualização 2026): duração, ganchos, engajamento, séries, testes; mistura trechos antigos e atuais.
- “Mais de 15 dicas para crescer no YouTube Shorts” — Buffer (2024): storytelling, SEO, comunidade, marca, testes, promoção cruzada.
- “Como Conseguir Mais Visualizações no YouTube Shorts: Um Guia Prático” — artigo de David Park (2026): ganchos, edição, produção em lotes e IA; estimativas de algoritmos não tratadas como fatos.
- “Algoritmo do YouTube Shorts explicado + dicas para crescer em 2026” — artigo de Gretchen Oestreicher / dados atribuídos à Metricool (2026): retenção, distribuição, métricas e conteúdo inautêntico; estatísticas do artigo precisam de verificação independente antes de virar regra.
- “Compreendendo os curtas do YouTube” — guia associado ao CapCut: roteiro, edição, categorias; inclui limites/formato desatualizados.
- “Guia do YouTube Shorts – 10 dicas para expandir sua marca no YouTube Shorts” — artigo de Sapna Singhal (2024): originalidade, som licenciado, SEO, análise, colaboração.

### Fontes oficiais conferidas em 2026-11-13 (prevalecem em caso de conflito)

- Duração, formato e reivindicações: https://support.google.com/youtube/answer/15424877?hl=pt-BR
- Descoberta e sinais do Shorts: https://support.google.com/youtube/answer/11914225?co=YOUTUBE._YTVideoType%3Dshorts&hl=pt-BR
- Métricas do Studio: https://support.google.com/youtube/answer/12942217?co=YOUTUBE._YTVideoType%3Dshorts&hl=en
- Mudança das visualizações em 2025: https://support.google.com/youtube/thread/333869549?hl=en
- Políticas de monetização / conteúdo inautêntico: https://support.google.com/youtube/answer/1311392?hl=en
- Divulgação de conteúdo sintético: https://support.google.com/youtube/answer/14328491?hl=en-GB
- Monetização de Shorts: https://support.google.com/youtube/answer/12504220

**Manutenção:** checar fontes oficiais periodicamente; anotar revisões antes de alterar regras de duração, monetização e copyright.