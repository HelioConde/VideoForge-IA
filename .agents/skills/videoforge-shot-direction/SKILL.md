---
name: videoforge-shot-direction
description: Direção de tomadas e cinematografia do VideoForge-IA. Use para enquadramento, foco de câmera, continuidade espacial e planejamento visual de episódios sem gerar poses obrigatórias.
---

# Direção de tomadas — enquadramento, intenção e continuidade

## Entrada obrigatória
Leia `AGENTS.md`, `docs/CONTRATO-CAMADAS-GERADAS-PELO-PROXY.md`, o roteiro/manifesto do canal, a Bíblia Visual com SHA, o último checkpoint e o plano de câmera. Em Alchemy Lab EP01 use `canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/PLANO-CAMADAS-CAMERA-EP01.json` (40 tomadas, C01-P01 tela preta, 39 tomadas visuais), `direcao-cinematografica-planos.json` e `videoforge/cinematic_direction.py`. Não substituir a contagem das 40 por documentos históricos de 37.

## Trabalho
1. Para cada tomada, especifique objetivo dramático, personagem/objeto focal, elenco realmente visível, plano (aberto/médio/detalhe), ângulo, composição 9:16, duração absoluta em frames e continuidade com tomada anterior/seguinte. Escolha foco narrativo; não faça zoom gratuito.
2. Defina a **imagem-mãe própria para a tomada**, usando as referências SHA da Bíblia Visual. Close que revela pixels/anatomia ausentes precisa de nova imagem-mãe via proxy, **não crop ampliado de um personagem distante**.
3. Planeje `camera.json` com posição, foco inicial/final, mudança de profundidade/rack focus, trajetória de dolly/tilt/pan e área de segurança. Movimento de câmera não substitui atuação articulada e não pode deformar a imagem.
4. Planeje planos de reação, estabelecimento e continuidade espacial com linhas de olhar, eixo de ação, alturas de personagem, direção das armas, contatos físicos, figurino, iluminação e objetos canônicos. Garanta que guardas seguram lanças **pela base**, não perto da ponta.
5. Requisite **background e personagens/objetos separados gerados pelo proxy** usando a cena-mãe como referência; recortes/máscaras locais são ferramentas de QA, não assets animáveis.
6. Envie ao [rig 2D](../videoforge-rig-2d-three/SKILL.md) as exigências de foco e movimento; ao [QA](../videoforge-qa-and-checkpoint/SKILL.md), a lista de checks de continuidade. Se houver áudio, combine pontos de corte com [áudio e montagem](../videoforge-audio-editing/SKILL.md).

## Saída e bloqueios
Entregar tabela de tomada/frames/enquadramento/foco/referências SHA/elementos visíveis/transition e dúvidas de identidade, com paths no próprio canal. Uma descrição de plano não significa que a arte existe. Não gerar nem promover aprovação humana fictícia, MP4 oficial ou YouTube. Manter C01-P02 sem rig enquanto a mãe V3/V4 e o bocal da bainha não forem aprovados.

Referências técnicas: `videoforge/cinematic_direction.py`, `motion-remotion/src/cinematic-timeline.ts` e `motion-remotion/src/cinematic-episode.tsx`. Remotion determina o tempo exclusivamente por `useCurrentFrame()` e FPS fixado.
