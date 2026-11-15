# Direção corrigida pelo usuário — C01-P03: somente respiração sutil

**Data:** 15/11/2026. **Status:** regras de aceitação e plano de correção registrados; **AINDA NÃO IMPLEMENTADOS NA ANIMAÇÃO V3**. Ler [pesquisa de bibliotecas/skills](../../../../docs/PESQUISA-SKILLS-BIBLIOTECAS-RIGGING-2D-2026-11-15.md), [estado atual](ESTADO-ATUAL.md), [histórico](HISTORICO-DESENVOLVIMENTO.md) e [manual global](../../../../docs/MANUAL-PRINCIPAL-ANIMACAO-2D.md) antes de alterar código.

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
- ⏳ **Não foram editados keyframes, sprites, máscaras, tests nem workflow de render nesta etapa de arquivamento.**
- ⏳ Ainda falta preparar V4, aplicar correções, renderizar e obter aprovação visual.

**Próxima ação exata:** abrir branch de correção C01-P03 V4, congelar braço/pulso/perna/bota/lanças, corrigir máscara do Aldric sem criar pixels, implementar somente respiração sutil e novos testes de pose ancorada/recortes; renderizar MP4 técnico e inspecionar quadro a quadro. Manter C12 separada e bloqueada enquanto faltarem os ZIPs originais.
