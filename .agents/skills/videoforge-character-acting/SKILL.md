---
name: videoforge-character-acting
description: Planejar e ajustar poses, timing e movimento secundario de personagens VideoForge quando a animacao parece mecanica ou nao expressa a acao do roteiro.
---

# Atuação e timing de personagens

Use o roteiro e a identidade visual aprovados da tomada. Reutilize a timeline e o FPS do projeto. Não reescreva a cena nem altere assets para compensar uma ação mal planejada.

Defina o que o personagem quer comunicar e quais poses tornam isso legível. Planeje antecipação, gesto principal, contato, pausa e acomodação quando servirem à cena; não imponha todos esses momentos a qualquer ação. Registre frames, pose-chave, olhar, controle responsável e relação com fala/objeto.

Valide primeiro a silhueta e a leitura de poses bloqueadas; ajuste espaçamento e curvas depois. Uma pausa deliberada pode comunicar mais que oscilação contínua. Cabeça, mão, corpo e olhar não precisam começar e terminar juntos. Evite compartilhar uma única curva por conveniência quando houver intenções distintas.

Preserve contatos exigidos pelo gesto. Dê a cabelo e roupa atraso e amplitude coerentes com o movimento principal, mantendo raízes/costuras presas; não aplique a mesma senoide a todas as peças. Não acrescente tremor, respiração ou piscadas apenas para que tudo se mova.

Implemente poses em função do frame absoluto usando o motor existente. Não use relógio, timers ou estado acumulado; interpolação correta não substitui intenção artística. Consulte [contatos e deformação](../videoforge-rig-2d-three/references/contacts-and-deformation.md) somente quando mexer nesses controles.

Entregue uma tabela curta de poses/frames e uma comparação da mesma ação antes/depois. Para julgar naturalidade, assista à prévia completa, não apenas stills. Siga o workflow autorizado de preview; diferencie teste mecânico, prévia técnica e tomada visualmente aprovada. A skill não concede aprovação humana nem autoriza publicação.

Origem: procedimento próprio do projeto, 17/11/2026. Mecanismo de animação: [ThreeCanvas](https://www.remotion.dev/docs/three-canvas). Verifique APIs contra o lockfile antes de usar exemplos de versões novas.
