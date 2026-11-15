**V2 ativo (15/11/2026):** 14 cenas / **40 tomadas** / 39 com arte própria + C01-P01 preta; 4890 frames. Revisar sempre `roteiro.json`, `remake-ep01-planos.json` e checkpoint antes de reutilizar material. Novos inserts C01-P05, C08-P04 e C12-P04 não possuem PNG aprovado; preservar rig C01-P02. Este bloco prevalece sobre números históricos de 37 tomadas.

---
name: videoforge-dorama-remake
description: Retome e programe episodios do dorama Alchemy Lab no VideoForge IA usando o manifesto V2, o checkpoint mestre, workflows GitHub e bibliotecas existentes. Use em toda demanda de escrever, gerar, corrigir ou animar o EP01.
---

# Skill — diretor e gerente autonomo do EP01

Esta skill e **local do VideoForge IA** e nao substitui a [documentacao oficial do Remotion](https://github.com/remotion-dev/skills/tree/7e541aa4d7361dfaca0780a565a47307eb7bdfbb/skills/remotion-best-practices). Primeiro aplicar `AGENTS.md` e `docs/MANUAL-PRINCIPAL-ANIMACAO-2D.md`.

## Checklist executavel por agentes

1. Ler `canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/ESTADO-ATUAL.md`, `estado-atual.json`, `autonomy-policy.json`, `remake-ep01-planos.json` e o historico. **Nunca** recomecar producao aprovada ou alterar V5/C12 historicos.
2. Executar `python -m videoforge.remake_starter --output output/remake-shot-queue.json`. Ler cada `task_fingerprint` e a etapa pendente; nao reenviar mesmas imagens com SHA confirmado.
3. Reutilizar `videoforge/cinematic_direction.py` para planos/angulos e `videoforge/production_scenes.py` para imagem-mae por tomada. Usar `videoforge/remake_reference.py` para a ancora canônica com SHA do repositorio, jamais arte V1 trocada.
4. A autorizacao permanente do responsavel em 15/11/2026 permite chamadas de IA/imagem necessarias **para este EP01** sem pedir nova aprovacao por chamada. Aplicar `autonomy-policy.json` (maximo UMA chamada faturavel por workflow, sem teto total editorial). Onde faltar referencia real, gerar candidata quando o coordenador liberar, arquivar e solicitar revisao visual; nunca aprovar identidade automaticamente. Se 429, falha ambigua ou risco de duplicacao, registrar e interromper nova chamada ate diagnostico.
5. Para cada tomada, separar RGBA em `body-no-head`, `head-open/closed`, cabelos, capa, bracos, props e underlays reais conforme necessario. Nunca adicionar objetos invisiveis por imaginacao.
6. Criar rig com `motion-remotion/src/rig-three-scene.tsx`, `rig-three-math.ts` e `@remotion/three`. Em `C01-P02`, usar `remake-sword-motion.ts` e `remake-sword-rig.tsx` (mao, lâmina e bainha independentes). Primeiro validar arquivos PNG e sua recomposicao.
7. Verificar quadro neutro, contatos, malha, olhos, cabelo, capa, fundo, continuidade, 30fps, camera 9:16, audio e SHA. Registro do estado tecnico ≠ aprovacao artistica.
8. Atualizar o checkpoint mestre + `estado-atual.json` + `HISTORICO-DESENVOLVIMENTO.md` no mesmo commit com data, run, paths, SHA, QA, bloqueios e proxima acao. Sem aprovacão publica, nunca publicar no YouTube.

## Base reutilizada

- Bibliotecas JA INSTALADAS: Remotion 4, React, Three.js, React Three Fiber e @remotion/three; nao fazer `npm install` em cada render.
- Padrao oficial externo: [Remotion Skills — pinned commit](https://github.com/remotion-dev/skills/tree/7e541aa4d7361dfaca0780a565a47307eb7bdfbb); ler `remotion-markup` (3d, multi-scene, timing e audio), `remotion-render` e `remotion-best-practices` conforme a tarefa. **Referencia documental, nao executar instalador remoto no workflow**.
- Codigo local: `videoforge/remake_starter.py`, `videoforge/remake_autopilot.py`, `motion-remotion/src/rig-three-scene.tsx` e `motion-remotion/src/remake-sword-rig.tsx`.
- Na falta de imagem, implementar apenas scripts, testes e contratos; nunca gerar PNG preto de preenchimento e chamar de arte aprovada.
