# Correção do rosto transparente e das frestas na capa — Otaku Multicena

## Causa confirmada em código e PNG

A transição da piscada usava `opacity=1-blink` para a cabeça aberta e `opacity=blink` para a cabeça fechada. Nos quadros 38 e 42, as duas imagens RGBA com `opacity=0.5` causam **alfa composto de aproximadamente 0.75**, mesmo sobre uma face opaca. Isso deixa o fundo aparecer pelo rosto. Não é necessário regenerar a imagem de olhos fechados — os sprites aprovados podem ser reutilizados.

A separação antiga da capa apagava pixels de `character-main.png` na área de sobreposição (`cape_alpha`), mas não reconstruía a roupa nem a pele atrás da capa. Sob movimento, abrem-se frestas na união da gola, peito e ombro. O novo comportamento de vento do `capeFront` ainda movia a região próxima ao broche.

## Alterações

1. **Cabeça sempre presente:** `head-open.png` é renderizado em opacidade total durante todos os quadros; somente `head-closed-ai.png` entra com `opacity=blink`. Nos quadros intermediários, nenhum dos dois estados remove a base do rosto. O motor antigo continua como fallback quando não há `headClosed`.
2. **Alfa validado:** `rig_draft_preview.py` confere pixel a pixel que `head-open.png` e `head-closed-ai.png` usam exatamente os mesmos valores de alfa. Se a edição de IA modificar a transparência do rosto, o render é bloqueado.
3. **Placa de proteção localizada:** `seam-underlay.png` contém exclusivamente pixels RGBA já existentes em `character-main.png`, recortados por `seam_underlay_polygon` com borda suavizada. Ela fica **atrás** das duas capas e do corpo, protegendo apenas a área do pescoço/peito/broche contra frestas — não mantém uma segunda capa inteira e não altera cabelo ou olhos.
4. **Gola frontal fixada:** `capeFront` tem atenuação progressiva da oscilação perto do broche. As pontas continuam reagindo ao vento, mas a parte presa no ombro não se desprende.
5. **Validações e regressão:** hashes SHA-256 do novo PNG, identidade da cena, dimensões, quantidade de pixels de origem, quadros intermediários da piscada, ombro fixo, malha da capa e status de rascunho. O fluxo [`rig-hair-preserve.yml`](../.github/workflows/rig-hair-preserve.yml) refaz os sprites da cena original, reaproveita os olhos IA já arquivados e renderiza MP4 sem novas chamadas à IA.

## Limitações

A placa de proteção usa o tecido original como camada *atrás* da capa dinâmica. Durante movimentos amplos, pode aparecer uma dobra estática sob a malha — preferível a um buraco transparente, mas **não equivale a reconstrução anatômica completa**. Em movimento mais forte, o correto será reconstruir ombro/peito/costas ocultos ou usar malha com oclusão baseada em profundidade.

Nenhuma aprovação visual ou publicação automática: `human_visual_approval=false`, `publishable=false`. O objetivo da prévia é confirmar que os quadros 37–43 não tornam o rosto translúcido e que o broche/pescoço não ficam com falhas durante as rajadas (frames 55, 95 e 190).

Este patch mantém separados o cabelo integral, a capa traseira/frontal e os olhos editados originalmente, sem geração de arte adicional.

## 13/11/2026 — Segunda correção: fresta ENTRE as duas metades da capa

O patch anterior preservava pixels do corpo sob a gola, mas não preenchia a fronteira entre a malha frontal e a traseira. Quando vento, atraso e intensidades diferentes moviam as metades em posições distintas, os limites complementares do recorte expunham fundo.

- Em `videoforge/rig_candidate.py`, `_cape_split` agora aceita `cape_seam_overlap_px` com margem bilateral calculada por dilatação em dois passes (O(largura × altura)). As duas partes compartilham uma faixa dos MESMOS pixels originais de `cape.png` ao redor da fronteira, em vez de recortes mutuamente exclusivos.
- O plano de `otaku-br/videos/teste-proxy-20261113/rig-plan.json` ativa uma margem de **36 px**; planos antigos sem a chave permanecem com a divisão antiga.
- Os testes `test_cape_seam_overlap_*` cobrem continuidade da faixa de tecido, preservação RGBA e rejeição de margens inválidas.
- O rosto continua sobre uma base opaca fixa e a proteção localizada da gola permanece. **Sem nova chamada de IA, sem aprovação humana, sem publicação.**

**Importante:** alterar o código não atualiza automaticamente o MP4 antigo. É necessário executar novamente `rig-hair-preserve.yml` (workflow_dispatch) e inspecionar especialmente os frames 55, 95 e 190. Mesmo com essa correção, a aparência final de uma capa com partes animadas separadamente exige revisão humana; não afirmar aprovação visual sem examinar o novo render.
