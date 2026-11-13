# Correção: preservar cabelo inteiro enquanto a capa usa malha separada

**Cena:** `otaku-br / teste-proxy-20261113 / cena-01`

## Origem do erro

O sprite `character-main.png` da cena original tem **todo o cabelo**. O corte não veio da animação da capa: a máscara manual `head_polygon` usada para extrair `head-open.png` deixava pontas e mechas fora do polígono, enquanto as regiões da cabeça eram apagadas do `body-no-head-no-cape.png`. O resultado removia mechas no Remotion.

## Correção aplicada

- `canal/otaku-br/videos/teste-proxy-20261113/rig-plan.json` adiciona `head_full_polygon`, um **novo contorno alinhado visualmente ao PNG de origem** que abrange fios na testa, topo, laterais e nuca; o contorno antigo fica apenas para compatibilidade.
- `videoforge/rig_candidate.py` passa a extrair a cabeça com o contorno integral e compara **alfa do próprio personagem original** em `hair_guard_bbox`. Recusa a cena se mais de 0,02% do alfa visível na região protegida for eliminado. O critério impede a regressão do recorte anterior.
- `videoforge/rig_hair_repair.py` reaproveita o `head-open.png` e `head-closed-ai.png` gerados anteriormente e armazenados em `rascunhos/olhos-fechados-ia/`. Confere SHA-256, canal, cena, original e proveniência, então aplica **somente os pixels previamente alterados nos olhos** sobre a cabeça nova, com o cabelo intacto. O código rejeita qualquer alteração fora das máscaras de olhos e não faz chamadas a IA.
- A capa continua separada nas duas camadas, `cape.png` e `cape-front.png`, com a mesma simulação de vento do [motor atual](VENTO-CAPA-REMOTION.md). A cabeça continua permitindo micro-rotação.
- `tests/test_rig_candidate.py` cobre preservação do contorno original, falha para máscaras cortadas e reaproveitamento de olhos sem apagar cabelo.
- O workflow [`rig-hair-preserve.yml`](../.github/workflows/rig-hair-preserve.yml) usa os **PNGs originais do artifact 43437992955** e os **olhos de IA já salvos no próprio canal**. Gera PNGs corrigidos e MP4 de 8 segundos 1080×1920, além de uma versão 540×960 compatível com navegadores. Não requer inferência nem upload ao YouTube.

## Verificar visualmente

Comparar os quadros 0 e 40 (olhos abertos/fechados) com 55, 95 e 190 (rajadas de vento), prestando atenção a mechas soltas, silhueta no alto da cabeça, junção da nuca com o ombro e áreas da capa sobrepostas. O guard de alfa é apenas um teste estrutural de preservação da arte; **a aprovação visual ainda precisa acontecer**.

A correção não reconstrói os ombros ou costas escondidos pela capa, nem promete uma simulação física de colisão. Por isso mantém `human_visual_approval=false`, `publishable=false` e `youtube_uploaded=false` em todas as prévias.

## Regra permanente

A existência da capa separada não justifica cortar cabelo. Toda máscara da cabeça deve englobar **as mechas originais inteiras**, e o rosto de olhos fechados deve alterar apenas as regiões dos olhos. Nunca regenerar personagem inteiro quando há sprites originais com SHA verificado.
