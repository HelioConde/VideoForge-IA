# Estratégia editorial — Emanuelly Kids (conteúdo infantil original)

> **Plano editorial, não execução.** Pesquisa de trends, vidIQ, geração de imagens, narração, Analytics e publicação são integrações futuras. Não criar candidatos, reservas, históricos ou métricas fictícios. Ler antes: `README.md`, `AGENTS.md`, `docs/ARQUITETURA.md`, `docs/REGRAS-EDITORIAIS.md`, `docs/ESTRATEGIA_SHORTS.md`, `canal/README.md`, `canal/<id>/README.md` e histórico **do próprio canal**.

## Regra máxima: Fofinhos é de gestão exclusiva do proprietário

**FOFINHOS / FOFINHO** é a série principal, mas **somente o usuário organiza** seus episódios, títulos, continuidade, personagens, cronograma e decisões criativas. O sistema **não pode sugerir, reservar, reescrever, gerar, alterar, descartar, publicar, dar continuidade nem usar personagens/arte da série** por iniciativa própria. Apenas agir sobre Fofinhos quando houver **pedido específico do usuário sobre a série**. Bloquear correspondências e nomes similares para evitar tocar inadvertidamente em Fofinhos. Demais temas infantis devem ser **separados**, com personagens próprios.

## Posicionamento e meta

Canal **feito para crianças**, com imagens de IA em histórias originais, educativas e lúdicas, linguagem simples e ritmo compreensível. Evitar formatos sensacionalistas, repetitivos ou superestimulantes. Oportunidades devem ser investigadas em tendências **apropriadas à idade**, não copiadas indiscriminadamente de vídeos infantis populares.

- **Público-alvo:** crianças e famílias brasileiras; confirmar faixa etária editorial antes de executar produção específica. Até isso, manter escolha conservadora de linguagem e temas.
- **Proposta:** entretenimento com gentileza, imaginação, pequenos desafios de observação, amizade e aprendizagem, sem pedir dados pessoais, comentários ou contato com crianças.
- **Pilares iniciais a testar fora de Fofinhos:** 35% histórias curtas com animais/personagens originais, 25% curiosidades e descobertas adequadas à idade, 20% jogos narrativos/observação, 20% habilidades socioemocionais (amizade, cooperação, lidar com frustrações).

## Radar de temas infantis

Investigar demanda agregada de famílias/responsáveis em buscas YouTube e Google Trends (quando dados forem apropriados), calendário cultural/escolar do Brasil, temas educacionais populares, livros e materiais infantis em domínio público/licenciados, e conteúdos públicos de canais infantis, sempre com revisão humana. Tendência popular para adultos **não** é automática para crianças. Não depender de comentários, posts de Comunidade, notificações ou cards — esses recursos podem ser desativados em conteúdo marcado como infantil.

## Formatos e exemplos de teste (fora de Fofinhos)

- “A capivara que aprendeu a dividir os brinquedos” — história inédita e positiva.
- “Onde está a estrela azul?” — pequeno jogo visual com solução no vídeo.
- “O passarinho que tinha medo de tentar” — cooperação e superação sem moralismo excessivo.
- “As cores do jardim encantado” — identificação visual e imaginação.

Cada episódio deve ter começo, descoberta e solução. Evitar recompensas manipulativas, sustos intensos, violência, perigos imitáveis, temas sexuais, indução a compras e falsos fatos educativos. Adaptar duração à capacidade de compreensão; não esticar histórias apenas para atingir número de segundos.

## Arte, segurança e classificação

- Visual coeso por vídeo: cores agradáveis, personagens com fichas fixas, traço ilustrado uniforme, expressões claras, cenários calmos e transições sem flashes excessivos.
- **Nunca** reproduzir personagens, cenários, vozes ou prompts de Fofinhos em novos projetos independentes; criar outro universo visual.
- Produzir apenas artes/vozes adequadas ao público infantil, licenciadas ou originais. Revisar cada imagem para elementos estranhos, membros extras, expressões assustadoras e mensagens confusas.
- `canal.json.youtube.feito_para_criancas=true` deve permanecer consistente com a classificação real exigida. Recursos como comentários, cards, posts e notificações não ficam disponíveis nos conteúdos designados “para crianças”; **não usar CTA dependente deles**. Política: https://support.google.com/youtube/answer/9632097?hl=pt-BR e https://support.google.com/youtube/answer/2801999?hl=pt-BR.
- Não apresentar uma série ainda não autorizada como parte do universo Fofinhos.

## Pontuação de pauta (0–5 por critério)

Segurança e idade **25%**; clareza/valor infantil **20%**; história original sem tocar Fofinhos **20%**; consistência e viabilidade de IA **15%**; interesse de público/famílias com evidência **10%**; variação em relação ao histórico **10%**. Qualquer falha de segurança, classificação, direitos, originalidade ou separação de Fofinhos é veto.

## Aprendizado

Analisar dados agregados do canal quando autorizados, respeitando limitações de conteúdo infantil. Comparar retenção, visualizações engajadas e formatos, sem inferir o que crianças individuais “querem” por dados pessoais. Priorizar histórias úteis e seguras em vez de perseguir conteúdo sensacionalista.

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
