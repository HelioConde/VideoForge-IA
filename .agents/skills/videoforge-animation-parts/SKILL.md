---
name: videoforge-animation-parts
description: Preparar ou diagnosticar pecas RGBA para animacao VideoForge quando torso, juntas ou recortes ficam incompletos ou revelam buracos durante o movimento.
---

# Peças prontas para animar

Trabalhe no canal/shot e na fonte SHA definidos no manifesto. Leia o checkpoint e o [contrato de camadas geradas pelo proxy](../../../docs/CONTRATO-CAMADAS-GERADAS-PELO-PROXY.md), que prevalece sobre procedimentos históricos. As peças animáveis são imagens independentes geradas pelo proxy usando mãe e Bíblia Visual como referências; recortes, segmentação e máscaras locais servem exclusivamente ao QA. Preserve originais e versões anteriores.

Exija proveniência `proxy_generated_separate_image`, mãe/referências SHA, run, alfa real e placement verificável. Reutilize validadores compatíveis; um validador legado de recortes não prova conformidade com esse contrato.

Distinga `color_sample`, `animation_part` e `occlusion_mask` na análise. Uma ROI de histograma pode excluir bordados e sombras; ela não é automaticamente uma peça completa para animar. Esses rótulos são conceitos de revisão, não novos campos já aceitos pelo programa.

## Diagnóstico de torso cortado ou junta aberta

Compare fonte, alpha, crop, recomposição neutra e frame defeituoso, nessa ordem. Verifique se a fonte contém a área; se o alpha a remove; se crop/offset/pivô compartilham coordenadas; se parentagem e escala foram aplicadas duas vezes; se a camada vizinha ainda cobre a junta; e se câmera/frustum ou clipping ocultam a peça. Identifique o estágio responsável antes de alterar o contorno. Não esconda o defeito com zoom.

Para cada parte móvel, registre no formato existente: origem/SHA, tamanho do canvas, placement, ordem de desenho e geometria necessária à ação. Crop/offset são medidas de QA ou de um placement autorizado, não permissão para produzir sprites por recorte. Diferencie coordenadas locais e coordenadas do canvas original. Confira se a peça gerada contém áreas ocultas suficientes aos extremos da ação; rig/pivôs finais somente após aprovação e QA de recomposição.

Verifique a continuidade por trás da camada vizinha e o fundo revelado. Quando faltar geometria oculta ou fundo limpo, registre região e movimento bloqueados e prepare a correção via proxy, respeitando autorizações/custos vigentes. Não conserte sprite final recortando a mãe ou movendo pixels. Cada geração tem proveniência própria e revisão; não apagar bordados que pertencem à textura para simplificar uma máscara de QA.

## Entrega

Entregue peças candidatas ou diagnóstico com coordenadas, comparação visual, SHA e lacuna exata. Não promova aprovação humana nem libere produção oficial. Se as peças estiverem aptas ao teste, passe ao rig o manifesto e seus limites. Para o movimento, use a skill irmã [rig 2D](../videoforge-rig-2d-three/SKILL.md); para avaliar a sequência, [QA](../videoforge-qa-and-checkpoint/SKILL.md).

Origem: procedimento próprio do projeto, 17/11/2026; respeita o [manual de animação](../../../docs/MANUAL-PRINCIPAL-ANIMACAO-2D.md). Não depende de serviço ou runtime novo.
