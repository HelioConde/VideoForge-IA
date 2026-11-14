# Padrão visual e técnico — animação por camadas (VideoForge IA)

> Registro de implementação. O workflow **Spy x Family animado** usa desenhos vetoriais provisórios para provar a movimentação. Não representa sprites finais ou uso de IA generativa neste teste. O padrão vem do rig validado no piloto Otaku BR em `rig-hair-preserve.yml`.

## Fluxo canônico obrigatório — cena-mãe → camadas RGBA → rig → montagem

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

## Intensidade de movimento e piscadas (regra de qualidade)

- Movimento de personagem em espera: deslocamento vertical máximo absoluto **2,8 px no quadro 1080×1920**; preset `equilibrado` com amplitude de 1,5 px antes dos redutores de contato. Movimento horizontal máximo 1 px, rotação máxima 0,25°. Não aplicar bob de 8–12 px ou deslocamentos rápidos que criem sensação de flutuação.
- Câmera: reduzir o pan para 25–30% da intensidade anterior; não usar zoom para fingir que olhos, cabelos ou roupas estão se movendo.
- Olhos: **somente** com `eyes-closed.png` RGBA, extraído da mesma cena-mãe, SHA e região dos olhos validados; rosto-base continua com opacidade 1 em todos os quadros. A piscada é breve (aprox. 5 quadros), sem esmaecer a cabeça e sem inventar um novo rosto.
- Objetos independentes: opcional `animatedObjects` no manifesto Remotion somente quando existir sprite real transparente e o objeto tiver sido removido da imagem-base. Objetos agarrados à mão seguem o personagem; objetos do cenário recebem apenas micro movimento de até 1,5 px, quando fizer sentido. Não gerar movimentos em elementos inexistentes.
- O teste Spy Family cena 01 contém personagem RGBA de grupo e agora uma camada de pálpebras da Anya. **Ainda não** há rig individual de corpo, braços, cabelo e objetos; registrar sempre `rig_animado_aplicado=false` até que todas essas partes sejam produzidas e validadas.
- Usar workflow normal GitHub Actions por `push` ou `workflow_dispatch`; **não usar modo privado de cota/proxy** que anteriormente bloqueava as execuções. O proxy autenticado utilizado no runner é uma dependência técnica distinta de um "private workflow mode".

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
