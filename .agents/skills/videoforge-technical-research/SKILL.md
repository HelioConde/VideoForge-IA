---
name: videoforge-technical-research
description: Pesquisar com rastreabilidade bibliotecas, documentação, skills e práticas de produção de vídeo IA e avaliar compatibilidade, licença e custo antes de qualquer integração no VideoForge-IA.
---

# Pesquisa técnica — evidência, compatibilidade e licença

## Entrada
Ler `AGENTS.md`, `docs/BIBLIOTECAS-E-SKILLS-VIDEOFORGE.md`, `docs/CONTRATO-CAMADAS-GERADAS-PELO-PROXY.md` e, quando houver animação, `docs/MANUAL-PRINCIPAL-ANIMACAO-2D.md`. Definir problema exato, versão/lockfile atual, documentação oficial, riscos e resultado mensurável. Priorizar reutilizar Remotion/Three.js/React Three Fiber já presentes.

## Checklist de pesquisa
1. Começar pelas fontes primárias atuais (documentação do fabricante, código original, testes e release compatível). Registrar URL, commit/tag/versão consultada e data da pesquisa.
2. Diferenciar **skill textual de instrução**, biblioteca realmente instalada, ferramenta externa e **agente executável**. Não escrever `installed` para uma URL apenas citada na documentação.
3. Auditar versão e compatibilidade: o VideoForge usa `@remotion/three` e `three` fixados em `motion-remotion/package.json`/lockfile. Não transportar API de versão diferente diretamente.
4. **Remotion é frame-driven**: `<ThreeCanvas>` usa `useCurrentFrame()`. Não usar `useFrame()`, `requestAnimationFrame`, `setAnimationLoop`, `THREE.Timer` ou `mixer.update(delta)` como relógio de render. Pode aproveitar conceitos de `AnimationClip`/pivôs/constraints **somente** se amostrados como função pura de frame/FPS; validar ordem reversa e random-access.
5. **Auditar licença de arquivo e repositório separadamente**. Há divergência observada entre o campo `license: MIT` da skill OpenMontage Character Rigging e a licença **AGPL-3.0** do repositório principal (17/11/2026). Até resolver escopo jurídico, utilizar apenas princípios gerais e links, **sem copiar código**. CloudAI-X Three.js Skills e arjun988 Blender Skills mostram MIT no repositório, mas ainda exigem adaptação à arquitetura e licença de qualquer arquivo copiado.
6. Examinar custos/credenciais, execução de comandos remotos, alterações de workflow, lockfile, permissões, isolamento de canal e possibilidade de rollback. Não executar instaladores/scripts de terceiros automaticamente; não criar chamadas pagas apenas para fazer benchmarking superficial.
7. Apresentar decisão explícita: `adopt_existing`, `adapt_concepts_only`, `investigate` ou `reject`, com justificativa, testes de aceitação e efeito sobre o pipeline. Sem alegar ganho de qualidade/performance sem prova.

## Fontes para consulta, não instalação
- [Remotion ThreeCanvas](https://www.remotion.dev/docs/three-canvas) e [evitar flickering](https://www.remotion.dev/docs/flickering) — fonte primária do render determinístico.
- [CloudAI-X — Three.js Animation](https://github.com/CloudAI-X/threejs-skills/blob/main/skills/threejs-animation/SKILL.md) — boas ideias de keyframes/morph/IK; exemplo de loop é incompatível com o relógio do Remotion.
- [OpenMontage — Character Rigging](https://github.com/OpenMontageInc/OpenMontage/blob/main/.agents/skills/character-rigging/SKILL.md) — conceitos de pivôs/hierarquia; pacote/runtimes distintos e divergência de licença.
- [Blender Skills — Animation](https://github.com/arjun988/blender-skills/blob/main/.claude/skills/animation/SKILL.md) — blocking, antecipação e arcos como referências, não pipeline Blender/MCP para vídeos atuais.

Registrar descobertas no documento de pesquisa do projeto com data, URLs e versão, mas não instalar dependências, gerar PNG/MP4 ou publicar sem que a atividade correspondente seja realmente autorizada e executada.
