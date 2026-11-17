# Contrato obrigatório — camadas de animação GERADAS pelo proxy (17/11/2026)

**Prioridade máxima para arte e rig de todos os canais do VideoForge-IA.** Esta decisão do proprietário substitui qualquer frase anterior que aceite extrair/recortar personagens, objetos ou partes móveis de pixels da cena-mãe para produzir sprites finais. A cena-mãe **é referência**, não uma imagem da qual o aplicativo recorta o boneco para animar.

## Fluxo de produção

1. Consultar Bíblia Visual, identidade/roupas, cenário, objetos canônicos, histórico, SHA e roteiro da tomada. Gerar via proxy uma **imagem-mãe completa**, com todas as figuras e objetos visíveis, anatomia/contatos corretos e enquadramento definitivo.
2. Fornecer **essa imagem-mãe e as referências canônicas relevantes ao proxy**, com pedido específico para GERAR uma **nova imagem separada** por elemento animável. No lugar de `crop`, segmentação de pixels, máscara manual, OpenCV ou recortes automáticos, a IA deve **desenhar a peça isolada**, respeitando exatamente modelo, escala, orientação, perspectiva, roupas, cores, luz, ponto de apoio e posição da tomada.
3. Solicitar ao proxy os produtos independentes necessários:
   - `background-clean.png`: cenário **recriado sem pessoas, armas nem partes que se movem**, inclusive superfícies antes encobertas; canvas e ponto de vista idênticos à cena-mãe.
   - `characters/<id>.png`: cada personagem **gerado isoladamente** com fundo alfa verdadeiro (RGBA), sem duplicar cenários/objetos. Individualizar cada guarda, rei, rainha, princesa, Kael, carrasco e elenco que estiver no plano, sem misturá-los em um grupo.
   - `objects/<id>.png`: cada espada, bainha, lança, coroa, prop móvel **gerado isoladamente** em transparência verdadeira; manter geometria e detalhes canônicos (bocal, brasão, textura, materiais). Criar partes ocultas necessárias ao movimento, sem alterar as partes visíveis aprovadas.
   - `characters/<id>/rig-parts/<parte>.png`: gerar via proxy, **somente quando serão animadas**, cabeça, olhos abertos/fechados, boca, braços, mãos, cabelo/capa, roupas e partes de rig. Cada variação de olho modifica só olhos; pedaços ocultos podem ser completados para não abrir buracos ao mover. Sem biblioteca obrigatória de poses independentes.
4. Preservar o mesmo canvas ou um manifesto de `placement` verificável com as coordenadas exatas para realinhar RGBA sobre a mãe, **sem esticar ou deslocar arbitrariamente**. Cada saída terá ID, papel, SHA-256, imagem-mãe SHA, referências canônicas, run, método `proxy_generated_separate_image`, alfa, estado QA e status de aprovação.
5. Conferir os arquivos em separado E a recomposição. Testar fidelidade ao original, identidade, textura, iluminação, contatos, bordas, ausência de duplicações/halos, geometria ocultada, alinhamento, mãos e coerência de objetos. Se falhar, pedir **nova edição/geração via proxy** com restrições estritas, versionando a candidata anterior; não consertar sprite final movendo pixels ou fazendo recortes do frame.
6. Só depois de aprovação das peças e QA de recomposição criar `rig.json`, pivôs, ossos e malhas Three.js/Remotion; aplicar movimentos de personagem e de câmera, focos e profundidade. Render/publicação dependem dos gates existentes.

## Distinção entre ferramentas

- **Permitido**: usar máscaras, segmentação, comparação/diff, polígonos, crops e overlays **exclusivamente em QA e prévias**, para mostrar defeitos, detectar oclusão, conferir transparência ou medir desvios. Esses resultados não são a arte final animável.
- **Proibido como fonte do rig**: `pixel_mask_extraction`, `deterministic_cutout`, `manual_polygon_cutout`, `opencv_segmentation`, `crop_from_mother`, `alpha_by_color`, `partial_png_patch` sem geração independente pelo proxy. Mesmo recorte perfeito em RGB não tem geometria oculta e pode ficar com fundo/roupa presos à peça.
- **Permitido para corrigir imagem-mãe**: edições localizadas via proxy e patches de comparação, mas não promover o patch localizado diretamente a sprite animável.
- **Obrigatório**: se o proxy não conseguir gerar um PNG transparente verdadeiro, geometria oculta, mesmo ângulo ou escala consistente, registrar `rejected` e tentar uma nova candidata separada; **não declarar camada pronta com fallback para recorte**.
- **Sem teto artístico fixo** de imagens, personagens ou partes. Evitar repetir imagens idênticas/custos e nunca refazer imagem arquivada sem motivo; uma chamada por execução conforme política do projeto.
- **Nada de poses obrigatórias**: as peças são geradas para rig articulado a partir da tomada com o personagem no ângulo da imagem-mãe, não como folhas soltas de poses.

## Exemplo concreto: C01-P02, espada e bainha

A tomada C01-P02 mostra espada parcialmente desembainhada: a mão superior segura cabo; a inferior segura bainha **na frente do casaco**; a lâmina deve entrar na **abertura física** do bocal. Quando a imagem-mãe for **visualmente aprovada**, pedir ao proxy, em execuções independentes com referências e SHAs válidos:

1. Fundo do salão sem personagem, lâmina, espada e bainha.
2. Personagem isolado sem armas e com mãos adequadas a manipular objetos, ou mãos/antebraços como peças adicionais vinculadas ao personagem.
3. Espada completa isolada (não só fragmentos visíveis); cabo, guarda, lâmina e partes ocultas necessárias para desembainhar.
4. Bainha isolada, completa, incluindo bocal sem geometria alterada, e com contato fisicamente possível.
5. Se necessário, luva superior, luva inferior e antebraços como PNGs gerados separadamente, com pivôs/oclusão e contacto preservados.

**Os PNGs de máscaras V1 e o patch localizado V4 são evidência histórica, não fonte de rig.** As versões V3/V4 continuam candidatas à escolha, e a V4 alterou detalhes do bocal: não promover uma variante sem revisão da Bíblia Visual e aprovação de continuidade. Não gerar camadas V4 de forma automática antes da seleção/aprovação da imagem-mãe.

## Critérios mínimos por asset no registro

`{"generation_method":"proxy_generated_separate_image","source_mother_sha256":"<hash real>","asset_role":"background|character|object|rig_part","canvas":[941,1672],"alpha_expected":true,"identity_references_sha256":["<sha real>"],"placement_verified":false,"visual_approval":false,"rig_ready":false}`

Os campos só podem ser marcados verdadeiros após evidência. `QA` local não é prova de geração pelo proxy, e **um workflow com exit code zero não aprova o desenho**. Até confirmar a integração de todos os produtores com esse contrato, tratar produtores históricos de máscaras/recortes como **legado não apto a rig final**.
