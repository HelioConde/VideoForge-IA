# Contrato oficial EP01 — cena-mãe → camadas → rig → direção de câmera

**Regra corrigida em 17/11/2026 por orientação do responsável pelo projeto.** Este manual tem prioridade sobre instruções antigas que exigiam gerar uma biblioteca de 12 **poses isoladas** antes de começar as cenas. A Bíblia Visual com 42 referências e 9 reparos V2 é preservada e reutilizada. O objetivo é **produção de vídeo**, não uma coleção de imagens de poses.

## 1. Solicitar ao proxy a cena completa

Para cada tomada do roteiro, usar as referências SHA-verificadas da Bíblia Visual: personagens, expressões, figurinos apropriados, cenário, adereços e fonte de estilo. Gerar **uma única cena-mãe** mostrando tudo que deve aparecer **naquele enquadramento** e **naquele momento da história**, com perspectiva, escala, iluminação e relações físicas coerentes.

**Não gerar composição genérica para depois depender de zoom infinito.** Planos diferentes podem ter imagens-mãe diferentes, sobretudo planos de olho, mão, objeto e silhuetas, quando a resolução/foco não comportam um recorte seguro. Isso **não** é gerar pose isolada: é gerar a tomada final com seu enquadramento próprio.

Exemplo C01-P04: Kael ajoelhado, rei ao fundo, dois guardas laterais com suas lanças fazendo X. A mão de **cada guarda deve envolver, com polegar e quatro dedos, o terço inferior da própria haste** próximo à base. A ponta da lança aponta ao centro e para cima. **Nunca anexar V3/V4 rejeitadas como referência física**; usar guardas individuais e lança portátil V2.

## 2. Pedir ao proxy para GERAR CADA imagem separada (não recortar)

**Nova decisão do responsável em 17/11/2026.** A imagem-mãe serve como **referência visual e espacial** enviada ao proxy; os arquivos animáveis devem ser **novas imagens geradas pelo proxy** em pedidos independentes, e NÃO segmentações, máscaras de polígonos ou crops locais de partes da imagem-mãe. O contrato de maior prioridade está em [Contrato de camadas geradas pelo proxy](../../../../docs/CONTRATO-CAMADAS-GERADAS-PELO-PROXY.md).

1. **`scene-mother.png`** — quadro final completo, imutável, gerado primeiro a partir da Bíblia Visual.
2. **`background-clean.png`** — pedir ao proxy para **gerar o mesmo cenário vazio** e completar o que estava oculto por pessoas/objetos, sem mudar arquitetura, perspectiva, iluminação ou câmera.
3. **`characters/<identidade>.png`** — pedir ao proxy para **gerar cada personagem separadamente** em PNG RGBA com transparência verdadeira, respeitando identidade, roupa, expressão, escala, posição, luz, perspectiva e proporções da cena-mãe. Um guarda por arquivo, não grupos achatados.
4. **`objects/<objeto>.png`** — pedir ao proxy para **gerar individualmente** espada, bainha, lanças e todos os outros props móveis com transparência e geometria completa, incluindo partes antes ocultas que serão necessárias ao movimento.
5. **`characters/<identidade>/rig-parts/<parte>.png`** — quando houver movimento, pedir ao proxy para gerar também cabeça, olhos, boca, braços, mãos, cabelo, capa e partes articuláveis, preservando alinhamento com o personagem e a tomada. Não criar bibliotecas obrigatórias de poses soltas.
6. **`rig.json`, `camera.json`, `qa.json`** — coordenadas e SHAs, pivôs, hierarquia, profundidade/oclusão, ângulos e focos de câmera. Máscaras e recortes locais são permitidos **somente como ferramentas para QA/visualização de diferenças**, jamais como sprites finais para ossos.

**Cada solicitação ao proxy usa a imagem-mãe SHA-verificada mais as referências pertinentes da Bíblia.** Gerar novos pixels, em vez de apenas selecionar pixels existentes, é crucial para desenhar a parte escondida atrás de roupa, mãos, objetos e cabelo. Nunca inserir personagem, espada ou cenário de outro enquadramento desconectado.

**Invariantes:** reconstruir a composição da tomada, validar fidelidade das peças, espessura das armas, pegada da mão e oclusões, sem personagens duplicados, halos, buracos nem mudanças de rosto/roupa. Não aprovar a camada só por SHA, PNG válido ou diferença média RGB. Conservar a versão rejeitada e pedir nova geração específica caso a IA mude a identidade ou o desenho canônico.

Cada PNG gerado fica no canal com identidade, origem `proxy_generated_separate_image`, SHA do próprio PNG, SHA da mãe e das referências, job, estado de QA e decisão visual. **Os recortes antigos do C01-P02 são históricos e não são permitidos como fonte para rig.**

## 3. Animar pelo rig: sem etapa de poses obrigatória

Mover personagens **pelas peças independentes geradas pelo proxy com a cena-mãe como referência**: olhos/piscar, boca/lip-sync, pescoço/cabeça, tronco, antebraço, mãos, cabelo, capa, pernas, roupas e itens anexados aos pivôs corretos. Remotion e rig/malha 2D/Three.js compõem movimentos e continuidade entre frames.

Ação da lança: a haste portátil V2 é um objeto separado. Seu pivô/constraint deve ficar acoplado à mão do guarda no **terço inferior/base** durante toda a animação. Verificar frames extremos, transições e contato fechado de dedos. **Não substituir por lanceiro imóvel com haste flutuante.**

Para ajoelhar, sentar, girar, tirar capuz ou desembainhar, ajustar os pivôs das camadas existentes e a oclusão. **Se um movimento exigir anatomia que a cena-mãe não contém ou ficar visualmente impossível com rig**, refazer **a própria cena-mãe para aquele enquadramento**, com novas imagens separadas solicitadas ao proxy e vinculadas ao mesmo conjunto de referências; não instituir biblioteca de poses como pré-requisito.

## 4. Direção de câmera é obrigatória

A cada plano, **mudar o foco conforme o roteiro**. Alternar plano aberto, médio, detalhe, plongée/contra-plongée quando indicado, sobre o ombro, tracking e closes (inclusive objetos e olhos). Usar:

- **Push-in / pull-out** sem esticar pixels, movimento lateral/pan/tilt, travelling e parallax de background / personagens / primeiro plano.
- **Rack focus** simulado por profundidade de campo entre camadas: olhos → objeto, mão → lança, personagem → cenário. Não desfocar o alvo principal nem cortar olhos e dedos importantes.
- **Corte cinematográfico**, tempo por frame e continuidade do eixo para os 40 planos. Foco alternado em Kael, rei, guardas/lanças, Elara, carrinho, flor, espada etc. Evitar câmera permanentemente estática.
- Respeitar **9:16 1080×1920 a 30 fps** e a janela temporal do roteiro. Caso um zoom precise de pixels inexistentes, **uma nova imagem-mãe do close** é melhor do que ampliar uma cabeça de 100 pixels.

A direção antiga define 37 planos. **C01-P05**, **C08-P04** e **C12-P04** foram acrescentados ao plano novo, que usa como autoridade de tempo o `roteiro.json` (40 planos, 4.890 frames), evitando as três sobreposições da antiga direção.

## 5. Pipeline por tomada e gates

`Bíblia Visual (SHA) → composição completa no proxy → reconstrução de background → extração RGBA por personagem/objeto → QA de recomposição → rig/câmera Remotion → QA do MP4 → aprovação/publicação`.

**Não existe quantidade máxima editorial de cenas, elementos ou imagens.** O número é determinado pelo roteiro e pela complexidade real do vídeo. Um workflow técnico limita **uma tentativa cobrável por requisição** para impedir retrabalho/429, **não a qualidade**.

A lista das 12 poses antigas continua no histórico para rastreabilidade, mas está marcada **`legacy_pose_request_deprecated`**, sem disparar imagens. Seu antigo workflow executa somente validação, sem proxy. **Não usar a ausência dessas poses para bloquear a criação das cenas-mãe.**

Entretanto, não suprimir QA: usar fontes SHA, exigir pegada correta, verificar o contato/rig, registrar estados honestos e preservar a regra de não publicar cenas ainda não validadas. O bloqueio antigo de 40 cenas e o upload YouTube não são removidos automaticamente por este documento; a migração do gate deve ocorrer pela nova arquitetura, não pela aprovação fictícia de poses.

## Arquivos de referência

- [Plano operacional estruturado dos 40 planos](PLANO-CAMADAS-CAMERA-EP01.json)
- [Roteiro original](roteiro.json)
- [Direção de fotografia original dos 37 planos](direcao-cinematografica-planos.json)
- [Bíblia Visual e SHA](../../biblia-visual/GALERIA-EP01.md)
- [Estado real do episódio](ESTADO-ATUAL.md)
- Código existente: `videoforge/production_scenes.py`, `videoforge/production_scene_layers.py`, `videoforge/production_rgba_parts.py`, `videoforge/cinematic_shot_assets.py`, `videoforge/cinematic_frame_fit.py`.
