# Padrão visual e técnico — animação por camadas (VideoForge IA)

> Registro de implementação. O workflow **Spy x Family animado** usa desenhos vetoriais provisórios para provar a movimentação. Não representa sprites finais ou uso de IA generativa neste teste. O padrão vem do rig validado no piloto Otaku BR em `rig-hair-preserve.yml`.

## Regras obrigatórias para TODOS os personagens e cenas

1. **Consistência e origem:** construir uma bíblia visual única por episódio e manter cabelo, roupa, proporções, acessórios, escala, luz e olhos idênticos entre quadros e cenas; nunca alternar ilustração/fotorrealismo sem decisão explícita.
2. **Recorte e camadas:** fundo, corpo sem cabeça, cabeça sólida, olhos, roupas e elementos independentes. Não sobrepor duas vezes capa, cabelo, objetos ou roupa que já exista no corpo-base.
3. **Rosto opaco:** a piscada afeta **somente a forma do olho**, nunca a opacidade de pele/rosto. A base da cabeça permanece visível a opacidade 1 em todos os quadros. Olhos fechados devem combinar com o desenho original.
4. **Costura e tecido:** raízes de cabelo e manga/capa/casaco precisam compartilhar a sobreposição de tecido ou underlay; não podem aparecer frestas ou marcas de máscara. As juntas ficam ancoradas no pescoço/ombros.
5. **Vento e movimento:** rajadas sutis, amplitude variável pela distância ao ponto de fixação, atraso da ponta e movimento frontal menor que o tecido traseiro; não animar o casaco inteiro como uma placa rígida. Usar funções determinísticas por frame, sem tremores.
6. **Animação natural:** cabeça faz inclinação discreta, corpo respira, olhos piscam sem teleporte, cabelo responde suavemente. Movimentos de câmera são leves e não devem cortar cabeça ou pernas.
7. **Narrativa acima de número de cenas:** não limitar quantidade de cenas por número arbitrário; cada cena tem visual relevante para a fala e áudio sincronizado. Duração total, custos, direitos e QA continuam válidos.
8. **QA:** renderizar quadros da abertura, piscada e rajada; comparar limites de recorte, olhos, rosto, iluminação, consistência entre cenas, áudio, legenda e H.264/AAC. QA automático não substitui revisão visual humana.
9. **Publicação:** todo teste começa `publishable=false`, `youtube_uploaded=false` e `visual_review=pending`. Somente aprovar quando artes, direitos, narração e qualidade forem revisados.

## Referências de código

- `motion-remotion/src/mesh-rig.tsx`: piscada, cabeça sólida, malha de tecido, vento e proteção de costura.
- `videoforge/rig_candidate.py`: separação de capa frontal/traseira com faixa de sobreposição de 36px no piloto anterior.
- `motion-remotion/src/character-idle.ts` e `cinematic-motion.ts`: movimento suave de corpo/câmera.
- `motion-remotion/src/spy-family-rig.tsx`: **implementação de prova** com três personagens 2D vetoriais, sem sprites finais; utiliza os princípios anteriores e formas opacas.
- `.github/workflows/spy-family-animated.yml`: preparação de 16 áudios PT-BR, render com Remotion e relatório de QA de MP4; gera artifact sem YouTube.

## Estado do piloto Spy x Family

- Pasta: `canal/otaku-br/videos/spy-x-family-familia-de-mentira`
- Roteiro: `roteiro.json`; 16 cenas; título e SEO no `editorial.json`.
- Motor: Remotion + formas SVG. As 16 cenas têm poses/movimentos próprios e cenários programáticos (casa, escritório e escola).
- Limite atual: **não há imagens finais dos Forger nem rig RGBA real**. O teste vetorial é apenas a prova do comportamento e do áudio.
- Geração de imagens por IA: **nenhuma** neste workflow. Voz: espeak-ng offline provisória.
- Um MP4 só pode ser declarado gerado após GitHub Actions finalizar com sucesso, registrar SHA, duração e artifact real. Não reaproveitar o MP4 anterior como se tivesse o roteiro e animação novos.
