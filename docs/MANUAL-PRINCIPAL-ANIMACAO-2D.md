# MANUAL PRINCIPAL DE ANIMAÇÃO 2D — VideoForge-IA

> **REGRA DE MAIOR PRIORIDADE PARA TODAS AS ANIMAÇÕES DO PROJETO.**
> Base integral: pesquisa aprofundada de animação 2D por malha fornecida pelo usuário em 14/11/2026.
> Aplica-se a todos os canais, agentes, modelos, vídeos, cenas e workflows presentes e futuros.
> **NUNCA considerar movimento do PNG inteiro, pan/zoom de câmera, sprite-bobbing, filtros FFmpeg ou cartoon vetorial genérico equivalentes a um rig articulado.**
> Não confundir o estado do motor com aprovação da arte. Se os sprites reais faltarem, `pipeline_pendente`, não render final.

## 1. Objetivo, engine e licenciamento

Manter o **Remotion 4** existente, reutilizando a arquitetura `canal/<id>/videos/<video-id>/` e os workflows GitHub Actions. Usar **Three.js + @react-three/fiber + @remotion/three/ThreeCanvas** como motor principal para rig 2D híbrido. Three.js implementa vértices, malhas trianguladas e, futuramente, bones/SkinnedMesh e morph targets. Cabeça, braços, olhos, mãos e acessórios usam **sprites rígidos com pivôs**; cabelo, capa, tecidos e demais materiais flexíveis usam **malhas deformáveis**. Não trocar a engine para Spine, Live2D, Rive, PixiJS ou DragonBones por padrão; opções futuras precisam de justificativa de desempenho, licenciamento e autoria. Não instalar pacotes em cada render nem substituir a imagem GHCR legada.

- Runner: `ghcr.io/helioconde/videoforge-remotion-runner:rig-three-remotion4-v1`.
- Remotion 4, render sem GPU: **`--gl=swangle --concurrency=1`** inicialmente.
- `useCurrentFrame()` e `useVideoConfig()` são a fonte ÚNICA do tempo: sem `Date.now()`, `Math.random()` sem seed, `requestAnimationFrame`, `useFrame()`, `setTimeout` ou física stateful no render.
- FFmpeg/FFprobe são para áudio, QA, extração de quadros, multiplexação quando apropriado; **nunca** a engine principal de animação.
- Revisar licença comercial do Remotion antes de ampliar equipe/uso; Three.js é MIT. Evitar novos serviços pagos desnecessários.

## 2. Ordem de produção obrigatória — imagem-mãe e depois peças geradas pelo proxy

1. Gerar a **imagem-mãe completa**, visual consistente, mesma composição, estilo, pose, perspectiva, iluminação, vestuário e personagens. Registrar SHA-256 e proveniência por canal/cena.
2. Com a **própria imagem-mãe como referência da edição de IA**, gerar o `background.png` reconstruído sem personagens/objetos móveis; manter o mesmo canvas e preencher áreas ocultas.
3. Enviar a **imagem-mãe e referências canônicas ao proxy** e pedir **UMA NOVA IMAGEM separada para cada personagem e objeto animável**, em PNG RGBA verdadeiro, mantendo identidade, ângulo, escala, luz e alinhamento da cena. **Proibidos crop, segmentação, máscara por polígono ou recorte local como fonte final do rig.** Não gerar cabeça ou braço desconectados da referência da tomada.
4. **Pedir ao proxy que gere também imagens separadas das partes móveis** de cada personagem quando necessárias: `body-no-head`, `head-open`, `head-closed`, `hair-back`, `hair-front`, braços/mãos, roupas, tecido e capa. As peças devem ser desenhadas com referência SHA da cena-mãe e do personagem isolado, não extraídas por máscaras locais.
5. **Solicitar ao proxy a geração das regiões antes ocultas** (pescoço, ombros, pele, roupa, cenário, braços, lâmina inteira) como parte das imagens individuais; apenas pixels visíveis da mãe não bastam para a articulação.
6. O **background gerado pelo proxy** não pode conter personagens, armas ou outros elementos dinâmicos, e os sprites independentes não devem duplicar franja, cabelo, capa, roupa, mãos ou objetos. Não limpar a arte final usando recorte local: pedir correção específica ao proxy.
7. Gerar `rig.json` por cena com **proveniência `proxy_generated_separate_image`**, SHAs da mãe/referências e de cada PNG independente, bbox e placement no canvas da mãe, pivôs, z-index/oclusão, malha, amplitudes e revisão/QA. Otimizações de memória durante render não autorizam criar sprites animáveis por recorte do frame original.
8. Montar pose neutra e **comparar pixel a pixel com o original**, por `diff.png`, contact sheet e métricas (round-trip composition QA). Corrigir buracos, halos, membros duplicados, pele transparente e costuras.
9. Só então animar com Remotion/Three, renderizar, inspecionar e registrar artifact e QA. Sem publicar no YouTube sem autorização específica.

**Política de proveniência:** [Contrato obrigatório — camadas geradas pelo proxy](CONTRATO-CAMADAS-GERADAS-PELO-PROXY.md). Máscaras locais, recortes e `diff.png` são ferramentas de **QA**, não meios de produzir imagens finais para os ossos. O proxy deve gerar as peças independentes com RGBA, inclusive áreas ocultas.

## 3. Rig híbrido e controles de movimento

- **Cabeça**: sprite independente, fixado pelo pivô medido **no pescoço** (não centro da imagem), limite inicial **±2°**, sem torcer todo o tronco. Modelar underlay do pescoço, cabelo/ombros, sem abrir fendas.
- **Corpo**: respiração leve e eventual deslocamento localizado; **não** movimentar o grupo de personagens ou plano achatado como substituição do rig.
- **Piscada**: a versão aprovada pelo usuário edita **a MESMA imagem da personagem, mudando SOMENTE os olhos**. Para o rig, aplicar o mesmo princípio à imagem da cabeça: `head-open` e `head-closed`, iguais fora dos olhos (incluindo cabelo/franja/alfa); troca breve de 4–6 quadros ou keyframes 0→0,55→1→1→0,45→0. O rosto não deve ficar transparente. Não sobrepor um adesivo de pálpebras por cima do cabelo.
- **Sincronização**: antes/depois da troca aberta/fechada, pose e pivôs precisam coincidir exatamente. Usar easing/neutro se necessário, mas não fazer um salto entre frames; **não reiniciar fase de animação abruptamente**.
- **Cabelo/tecido/capa**: `BufferGeometry` com UV do sprite, malha 7×9 / 6×8 / 8×12 conforme asset, raízes costuradas fixas, ponta com onda procedural suave, atraso progressivo e rajadas não periódicas. Sem duplicar o material no corpo/base. Não aplicar capa/espada em cenas onde não existam.
- **Braços/objetos**: sprites independentes, pivôs medidos, posição vinculada à mão quando agarrados; IK de 2 bones pode entrar apenas depois que rig de cabeça/piscada/cabelo estiver validado.
- **Limites artísticos**: evitar saltos, tremor, bob exagerado, quebra de silhueta, bordas transparentes e transições geométricas improváveis. Para rig rígido começar em ±2°; para malha limitar por `rig.json`, com raiz fixa e deformação crescente até a ponta.
- **Sem estado acumulado**: cada vértice/pivô depende só de `frame/fps` e manifesto, gerando a mesma imagem quando um frame é renderizado repetidamente.

## 4. Ordem visual, máscaras e proteção da identidade

A ordem depende da cena, mas segue a hierarquia: `background` → materiais/cabelo traseiros → corpo e underlay de pescoço → cabeça e olhos → cabelo/franja à frente → tecido/capa frontal e membros/objetos conforme z-index → `foreground` → legendas. Uma capa pode ter partes atrás e à frente do corpo e deve ser dividida. Não reutilizar z-index do exemplo de aventureiro em Spy × Family.

PNG RGBA8 válido **não prova** que um sprite está corretamente separado. Além de alfa e SHA, revisar diferença entre original e recomposição, hotspots de cabelo/ombros, franjas, costuras, olhos abertos e fechados e cortes. Preencher `humanReview` como verdadeiro apenas após inspeção efetiva; caso contrário bloquear `rig`.

## 5. Testes obrigatórios (fail closed)

- **Frames exatos**: renderizar duas vezes frames `0, 30, 74, 76, 173, 175` e final; comparar pixels/hashes.
- **Atuação perceptível no enquadramento final (regras C01)**: SHA e movimento técnico de 50 pixels NÃO provam que o espectador verá a ação. Avaliar a amplitude de **pivôs reais** (cabeça, punhos, ombros, cabelo e roupa) e comparar quadros decodificados do **MP4 verdadeiro** na região do personagem, excluindo texto, legenda, zoom/pan de câmera e outras fontes de movimento falso. Conferir também o vídeo no tamanho final de exibição, especialmente no celular. Se o resultado parecer parado, rejeitar a atuação e revisar storyboard/articulação sem balançar o PNG inteiro.
- **Sem liberar exceção à regra de cabeça**: a rotação de até `2°` continua sendo o limite deste manual para rig aprovado. Um **rascunho técnico experimental** pode ser usado para diagnosticar atuação maior, mas deve ser marcado `humanVisualReview=false`, `publishable=false`, `officialVideoApproved=false` e registrar qualquer divergência; o teste não aprova amplitude acima do limite, nem autoriza preencher anatomia com pixels inventados. Corrigir underlays e obter revisão de rig antes de qualquer vídeo oficial.

- **Cabeça**: `abs(rotationDeg) <= 2`; pivot dentro da cabeça e coincidindo com pescoço/underlay real.
- **Piscar**: imagens realmente diferentes **somente** nas áreas dos olhos, frame aberto/fechado correto, rosto opaco e franja não alterada.
- **Malha**: linha superior costurada imóvel; pontas dentro do envelope permitido, sem triângulos degenerados ou fendas visíveis.
- **Oclusão**: franja sobre o rosto, capa sem cruzar indevidamente o peito/braço, mãos/itens respeitando z-index, sem haloes/clipping.
- **Recomposição**: `body-no-head + head + hair + cloth/objects` em pose inicial ≈ imagem original; gerar `diff.png` e métricas. Bloquear alto erro fora das máscaras.
- **Transparência**: verificar bordas no claro e escuro e áreas antes ocultas reconstruídas.
- **QA audiovisual**: resolução, duração, 30fps, H.264/AAC, narração feminina, legendas, áudio sincronizado, continuidade.
- **Procedência**: guardar IDs de artifact/run, source SHA, SHA por PNG e relatórios em `canal/<id>/videos/<video-id>/` e `output/<id>/videos/<video-id>/assets/<cena>/`.
- **Status**: `rig_animado_aplicado=false`, `video_oficial_do_programa=false`, `youtube_uploaded=false` até haver assets completos, rig real, QA e aprovação. Nunca simular validação humana.

## 6. Módulos oficiais, continuidade e roadmap

- Núcleo: `motion-remotion/src/rig-three-math.ts`; render: `motion-remotion/src/rig-three-scene.tsx`; raiz isolada: `motion-remotion/src/rig-three-index.ts`.
- Validação: `videoforge/rig_three_contract.py`; preparação e QA de render: `videoforge/rig_three_preview.py`; template: `modelos/camadas-animadas/rig-three.template.json`.
- CI: `.github/workflows/rig-three-smoke.yml` para sintéticos e `.github/workflows/rig-three-real-render.yml` **somente para sprites aprovados**.
- Primeiro MVP real: corpo separado, cabeça ±2°, piscada com a mesma cabeça editada, cabelo frontal em malha. Capa/roupa deformável **somente se existir** na cena. Depois acessórios, mãos, braços/IK e rig avançado.
- Primeiro alvo: `canal/otaku-br/videos/spy-x-family-familia-de-mentira`, cena 01, mantendo a imagem da Anya e a piscada já aprovadas, sem gerar personagem novo de aparência diferente.
- Se os PNGs do corpo sem cabeça/olhos/cabelo **não existirem**, o motor está testado, **mas a animação real da personagem continua PENDENTE**.

## 7. Hierarquia e conflitos com regras anteriores

**Este manual prevalece sobre outras recomendações de microanimação, câmera, eye-overlays, vídeo sem rig e templates legados.** O `AGENTS.md` e o `README.md` devem apontar diretamente para ele. Se documentos antigos instruírem a usar sticker de pálpebras, cabelo duplicado, FFmpeg para animar PNG ou bob do sprite inteiro como substituição de rig, essas instruções são **OBSOLETAS PARA PRODUÇÃO OFICIAL**. A regra nº 1 (produção via VideoForge-IA GitHub e sem publicar sem autorização), a política de orçamento, a separação por canal e a segurança seguem válidas.

**Fontes-base:** pesquisa aprofundada enviada pelo usuário sobre Three.js + @remotion/three, PixiJS, Spine, Rive, Live2D, DragonBones; composição híbrida; asset reconstruction/QA; `swangle` em GitHub sem GPU; manifesto com bbox/pivô; determinismo por frame. Ver também `docs/RIG-THREE-MALHA.md`.
