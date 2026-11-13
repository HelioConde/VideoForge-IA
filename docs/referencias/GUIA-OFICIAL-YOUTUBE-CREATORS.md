# YouTube Creators — pesquisa oficial aplicada ao VideoForge IA

**Consulta:** 13/11/2026. **Origem:** [YouTube para Criadores](https://www.youtube.com/intl/pt-BR/creators/) e páginas oficiais da Central de Ajuda. **Status:** orientação editorial consultada e sintetizada; **não** implica que agentes, Analytics, produção de vídeo ou publicação foram executados.

Este documento é complementar ao [catálogo de 23 cursos](CATALOGO-CURSOS-YOUTUBE.md), cujas aulas ainda **não** foram verificadas. É uma síntese própria de fontes oficiais, não uma cópia de artigos ou transcrições.

## Fontes oficiais

| Tema | Fonte |
| --- | --- |
| Portal e FAQ | https://www.youtube.com/intl/pt-BR/creators/ |
| Primeiros passos, Studio e configuração | https://www.youtube.com/intl/pt-BR/creators/how-things-work/getting-started/ |
| Comunidade, comentários, legendas e colaboração | https://www.youtube.com/intl/pt-BR/creators/how-things-work/building-community/ |
| Crescimento, recomendações, programação e Analytics | https://www.youtube.com/intl/pt-BR/creators/how-things-work/content-creation-strategy/ |
| Monetização e programa de parcerias | https://www.youtube.com/intl/pt-BR/creators/how-things-work/video-monetization/ |
| Diretrizes, direitos autorais, público infantil | https://www.youtube.com/intl/pt-BR/creators/how-things-work/policies-guidelines/ |
| Desempenho e recomendações | https://support.google.com/youtube/answer/141805?hl=pt-BR |
| Shorts de até três minutos | https://support.google.com/youtube/answer/15424877?hl=pt-BR |
| Monetização, conteúdo repetitivo e reutilizado | https://support.google.com/youtube/answer/1311392?hl=pt-BR |
| Transparência do uso de IA | https://support.google.com/youtube/answer/14328491?hl=pt-BR |
| Elegibilidade do Programa de Parcerias | https://support.google.com/youtube/answer/72851?hl=pt-BR |

## Aprendizados e recomendações para a futura operação

1. **Priorizar o espectador, não um suposto truque do algoritmo.** Os sistemas de descoberta consideram interesses, histórico de consumo e satisfação. Usar pesquisa para levantar hipóteses sobre o público; não prometer viralização.
2. **Embalar com honestidade.** Título, descrição e miniatura precisam corresponder ao conteúdo; escrever abertura envolvente desde os primeiros segundos, particularmente para Shorts.
3. **Usar métricas reais por canal.** Com acesso autorizado ao Studio/Analytics, analisar retenção, tempo médio assistido, impressões e CTR, espectadores novos/recorrentes, interesses do público e vídeos mais relevantes; anotar origem e data. Sem dados, registrar pendência e não inventar métricas.
4. **Aprender após a publicação.** Definir hipótese, objetivo e diferenças criativas antes de produzir; depois avaliar resultados reais, reconhecer incerteza e registrar aprendizados no histórico do canal.
5. **Cuidar da comunidade.** Considerar comentários e perguntas legítimas, legendas, playlists, cards/telas finais e postagens quando disponíveis e adequados ao canal. Evitar spam e pedidos de engajamento manipuladores.
6. **Controlar consistência e qualidade.** Manter aparência dos personagens, arte, narração e ritmo coerentes, mas garantir histórias e valor significativamente diferentes em cada episódio. Consistência visual não significa repetir enredo.
7. **Escolher cadência com base em qualidade e público.** Não há evidência de que publicar mais, por si só, garanta distribuição. Testes de duração e frequência exigem dados comparáveis.

## Matriz de responsabilidade para agentes futuros — não implementados

| Etapa | Checagem editorial | Onde documentar |
| --- | --- | --- |
| Pesquisar | Histórico do canal, assuntos parecidos, fontes, tendência confirmada, hipótese de público | `canal/<id>/editorial/` e `editorial.json` do vídeo |
| Roteirizar | Gancho, desenvolvimento, valor original, adequação do tema e revisão de fatos | `canal/<id>/videos/<video-id>/editorial.json` |
| SEO | Pesquisa, título, descrição, hashtag e ideia de miniatura honestos | `editorial.json` |
| Direção de arte/edição | Identidade consistente, narração e legendas legíveis, áudio e mídia com uso permitido | `editorial.json` e, quando existirem assets, `video.json` |
| QA/conformidade | Segurança, originalidade, direitos, IA, faixa etária, e prova do MP4/QA | Relatório técnico não versionado e parecer editorial |
| Avaliar | Comparar a hipótese com métricas coletadas depois da publicação real | Histórico do **mesmo** canal |

Não tratar a matriz como agentes ativos. O MVP ainda exige primeiro MP4 real verificável (90–180s, piloto Otaku Multicena) e não habilita publicação nem provedores pagos.

## Alertas normativos que não podem ser ignorados

### Shorts de 3 minutos e copyright

A página antiga do portal ainda contém referências desatualizadas a Shorts de 60 segundos. A Central de Ajuda informa que, para canais padrão, vídeos quadrados/verticais de até **3 minutos** enviados desde **15/10/2024** podem ser classificados como Shorts. Shorts **com mais de 1 minuto** sujeitos a reivindicação ativa do Content ID são **bloqueados globalmente** até que a reivindicação seja resolvida. O piloto de 90–180 segundos está dentro do limite de duração, mas isso não autoriza clipes de anime, músicas ou material de terceiros. Ver https://support.google.com/youtube/answer/15424877?hl=pt-BR.

### Não produzir em massa conteúdo repetitivo

Políticas oficiais de monetização exigem criação **original e autêntica**. Conteúdo gerado por IA de maneira genérica, repetitiva, com pequenas mudanças cosméticas ou baixo valor criativo/narrativo pode não ser elegível. Um formato consistente pode ser usado, desde que cada vídeo apresente contribuição substancial. Material de terceiros precisa de direitos e, se reutilizado, valor editorial significativo; adicionar comentários ou filtros não garante permissão ou monetização. Ver https://support.google.com/youtube/answer/1311392?hl=pt-BR.

**Regra proposta:** nenhum vídeo deve prosseguir sem registrar tema, assuntos relacionados, comparação com histórico e a diferença substantiva de seu valor narrativo, educativo ou analítico.

### IA, crianças e transparência

Em geral, o YouTube exige indicação para **conteúdo sintético com aparência realista** que represente fatos, lugares ou pessoas de modo alterado, além de determinadas músicas geradas por IA. Uso de IA para ajudar no roteiro, título ou edição simples não acarreta automaticamente a mesma obrigação. Conferir a página oficial e os controles de upload vigentes; a divulgação não substitui a conformidade. Ver https://support.google.com/youtube/answer/14328491?hl=pt-BR.

Conteúdo direcionado a crianças deve ser classificado corretamente, com atenção às políticas para público infantil. Para canais de anime, revisar a procedência de todas as imagens, vídeos e trilhas. Conferir direitos autorais e políticas antes de qualquer upload; não presumir que uso de trecho é automaticamente permitido.

### Monetização

Critérios de inscritos, horas e visualizações e recursos disponíveis podem mudar; consultar a Central de Ajuda e o Studio do **canal específico** ao tomar uma decisão. Não registrar monetização como ativa apenas porque um limite foi alcançado.

## Aplicação inicial por canal

- **`otaku-br` (Otaku Multicena):** temas inéditos, análise original, risco elevado de Content ID em trechos/músicas e Shorts >1 min.
- **`otaku-en` (Otaku Reframe):** tratar métricas e público de idioma diferente independentemente.
- **`gamer` (Conde Games):** diferenciação real entre episódios de jogos; títulos fiéis à experiência.
- **`manu-kids` (Emanuelly Kids):** segurança e classificação infantil, variedade narrativa, personagens consistentes.
- **`alchemy-lab` (Alchemy Lab):** avaliar nichos e formatos com pesquisa e dados, sem inventar resultados.

**Estas são aplicações planejadas, não diagnósticos reais dos canais.** Não misturar histórico, pautas, métricas ou índices de canais diferentes.

## Forma de consulta permanente

Ordem: `README.md` → `AGENTS.md` → `docs/ARQUITETURA.md` → `docs/REGRAS-EDITORIAIS.md` → `canal/<id>/README.md` e histórico → este guia e [catálogo de cursos](CATALOGO-CURSOS-YOUTUBE.md), conforme a tarefa.

Revalidar as fontes oficiais no momento da decisão, especialmente políticas e recursos que mudam. Preservar a hierarquia `canal/` (singular), sem novos diretórios concorrentes.
