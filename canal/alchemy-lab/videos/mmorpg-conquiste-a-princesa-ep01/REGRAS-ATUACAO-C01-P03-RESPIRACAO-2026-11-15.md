# Direção corrigida pelo usuário — C01-P03: somente respiração sutil

**Data:** 15/11/2026. **Status:** regras de aceitação implementadas na **V4**, [PR #57](https://github.com/HelioConde/VideoForge-IA/pull/57) integrado à main e [render técnico 43676630976](https://github.com/HelioConde/VideoForge-IA/actions/runs/43676630976) **SUCCESS**; **aprovação visual humana ainda pendente**. A V3 permanece histórico técnico reprovado visualmente. Ler [pesquisa de bibliotecas/skills](../../../../docs/PESQUISA-SKILLS-BIBLIOTECAS-RIGGING-2D-2026-11-15.md), [estado atual](ESTADO-ATUAL.md), [histórico](HISTORICO-DESENVOLVIMENTO.md) e [manual global](../../../../docs/MANUAL-PRINCIPAL-ANIMACAO-2D.md) antes de alterar código.

## Observações do usuário após assistir C01 V3

- **Braço direito de Kael:** está apoiado sobre sua perna. A rotação independente do braço/antebraço/punho na V3 ficou antinatural. **Remover os gestos desse membro** e conservar contato mão–perna. Atenção: com hierarquia em `kael.ombros`, somente zerar rotações locais NÃO garante contato na tela; considerar travamento em coordenadas globais e QA da mão.
- **Bota/pé direito:** a V3 trouxe uma articulação independente da bota e criou corte visível. **Travar bota e perna**, restaurando a silhueta neutra com os pixels aprovados; não usar bota como artifício para superar um limiar alto de pixels em movimento.
- **Respiração:** única ação expressiva principal de Kael: peito/ombros, movimento mínimo da jaqueta/cabelo e inclinação imperceptível da cabeça. **Menos é mais neste primeiro plano**; remover atuação de drama/cotovelos/flexão de tornozelo que contradiga a pose ajoelhada.
- **Lanças/guardas:** lanças devem permanecer rígidas e fixas, sem deformação, recorte solto, duplicação ou vazamentos; guardas permanecem praticamente imóveis. Consertar composição/máscara antes do novo MP4.
- **Rei Aldric:** cabeça aparece cortada. **A pose neutra precisa ter a cabeça inteira**, segundo a arte original aprovada. Não animar enquanto a máscara estiver incorreta; tratar como impeditivo de aprovação.
- **Câmera:** imóvel no teste do rig (sem simular vida com pan/zoom). **Não gerar novas imagens** e **não publicar no YouTube**.

## Orientação técnica da pesquisa (hipóteses para teste, não decisões já implementadas)

1. **V4 de C01, partindo da V3 existente:** reduzir/remover as 9 tracks anteriores conforme causa narrativa; registrar locks em `direcao-rig-remotion.json` ou documento de constraints correspondente. Não destruir o histórico V3.
2. **Fixação de contato do braço:** testar `world-space contact lock` do pulso/mão à perna e a possibilidade de desacoplar este membro do osso móvel `kael.ombros`. Evitar que o ombro arraste o apoio; se necessário, tratar a mudança como pequena deformação de jaqueta, não uma rotação do braço.
3. **Respiração determinística:** como primeiro candidato, amplitudes nativas de ombro/tórax de cerca de **±1 a 2 px**, cabeça até **0,5°**, malha de cabelo e jaqueta mínima; ajustar visualmente à fonte. A regra global de cabeça ≤2° permanece; 0,5° é **meta específica de C01**, não regra geral do motor.
4. **Não usar limiar da V3 como meta cega:** `C01_ACTING_STILL_TOO_SUBTLE_IN_REAL_MP4` e gate `16.000` pixels de ator foram úteis para diagnosticar a V1, mas induziram a animar membros que devem ficar parados. Para uma cena de respiração, usar gate **de movimento localizado na malha respiratória**, integridade de contato, máscara neutra e estabilidade temporal; não apenas contagem global de pixels.
5. **Máscaras existentes e underlays:** consertar cabeça do rei, lanças e corte da bota com pixels RGB/RGBA aprovados. Se não houver pixels ocultos reais, não recriar anatomia por IA: reduzir a amplitude ou reparar usando sobreposição verificável.
6. **QA de regressão:** comparar frame 0 com imagem-mãe aprovada e frames 30/55/75/89 com foco em máscara do rei, lanças, braço/joelho, bota, cabelo/gola. Medir estabilidade de regiões estáticas sob decodificação H.264, evitar falso sucesso por codec/legendas.
7. **Aprovação:** só pedir revisão humana após teste em 1080×1920, visualização em celular, sem corte de cabeça/pé e sem movimentação não motivada. C01 V3 **é tecnicamente validada, mas rejeitada visualmente para esta direção**.

## Ferramentas candidatas, com papel limitado

- [Three.js](https://github.com/mrdoob/three.js) + Remotion: permanecer no motor atual, criar constraints por junta/âncora e malha de respiração.
- [OpenCV](https://github.com/opencv/opencv) e [scikit-image](https://github.com/scikit-image/scikit-image): revisar máscaras, contornos, pixel diff e recortes.
- [spine-animation-ai](https://github.com/GenielabsOpenSource/spine-animation-ai): **estudar métodos de posicionamento** de partes; licença não comercial citada, não copiar código sem revisão.
- [claude-animated-shorts](https://github.com/mromidev/claude-animated-shorts/blob/main/SKILL.md): adaptar a organização de direção e QA, não esperar que corrija o rig automaticamente.
- Rev2D/Rigby2D/IKPy: **teste isolado opcional**, apenas depois da C01 voltar a uma pose neutra confiável.

## Estado de implementação na data do registro

- ✅ Pesquisa e novas regras visuais registradas no repositório.
- ✅ V3 original preservada para comparação e rollback.
- ✅ **Implementação posterior ao arquivamento:** C01-P03 V4 integrada na main no commit `4d010a92212ce77e9c7fbcf762537ecf0e732be2`; keyframes reduzidos a 2; mão e bota direitos fixos; rei, guardas e lanças copiados da imagem-mãe original, sem recortes-candidatos sobrepostos.
- ✅ [MP4 real](https://github.com/HelioConde/VideoForge-IA/actions/runs/43676630976) de 3 segundos gerado com gates técnicos aprovados; [relatório detalhado de qualidade](QA-C01-P03-V4-2026-11-15.md).
- ⏳ **Ainda falta avaliação visual humana da V4 e eventuais reparos finos de alpha**, e o episódio de 163s não foi concluído.

**Próxima ação exata:** assistir à prévia V4 já renderizada da `main` para confirmar a respiração, a mão encostada no joelho, a bota inteira, o rei com coroa íntegra e as lanças rígidas. A etapa técnica básica V4 já está concluída; corrigir somente problemas visuais remanescentes e não restaurar os nove gestos da V3. Manter C12 separada e bloqueada enquanto faltarem os ZIPs originais.
