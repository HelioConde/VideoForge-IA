---
name: videoforge-qa-and-checkpoint
description: Fazer QA verificavel de arte, rig Three.js, Remotion e workflows GitHub e manter memoria duravel por canal, sem apagar historico ou afirmar aprovacao falsa. Use apos cada geracao, render, erro ou correcao.
---

# Skill — qualidade, evidencias e memoria do VideoForge

1. Ler `AGENTS.md`, `docs/MANUAL-PRINCIPAL-ANIMACAO-2D.md` e `ESTADO-ATUAL.md` no canal antes de executar.
2. Confirmar bytes reais das imagens e MP4s, manifesto de origem, SHA, ID de workflow, paths e tamanho/frame count; nao tratar relatorio JSON, prompt ou fixture como imagem criada.
3. Inspecionar continuidade rosto/roupa/cabelo/cenario, 180 graus, geografia, membros e objetos; verificar camadas e reconstruir zonas escondidas para nao revelar transparencia.
4. Testar `python -m unittest tests.test_remake_starter tests.test_remake_autopilot tests.test_remake_cinematic_integration tests.test_remake_reference -v`; para movimento `node --test motion-remotion/tests/remake-sword-motion.test.cjs` (na pasta motion-remotion usar `node --test tests/remake-sword-motion.test.cjs`).
5. Nao executar chamada de IA paga, nem upload, nem marcar `human_visual_approved=true` automaticamente. `technical_qa_passed` e `human_art_approved` sao estados diferentes.
6. Para falha deterministica: identificar erro, aplicar correcao pontual, criar regressao, executar somente etapa afetada e registrar SHA/commit/run. Parar apos repeticoes improdutivas; 429/cota e consentimento nunca sao resolvidos forcando chamadas.
7. Atualizar **sempre** `canal/<id>/videos/<video-id>/ESTADO-ATUAL.md`, `estado-atual.json` e `HISTORICO-DESENVOLVIMENTO.md` com ultima validacao e proxima acao exata; arquivos anteriores nunca desaparecem sem justificativa e proveniencia.

Fonte oficial de boas praticas: [Remotion Agent Skills](https://github.com/remotion-dev/skills/tree/7e541aa4d7361dfaca0780a565a47307eb7bdfbb), apenas consulta e adaptacao compativel. Nao copiar codigos/skills de terceiros sem auditar licenca, versao e seguranca.

## C01-P02 — QA do empacotador automático

Ler `videoforge/remake_sword_pack.py` e `docs/C01-P02-PACOTE-ARTE-E-RIG.md` antes de validar. Arquivos reais só vêm de `assets/geracoes/<produtor>/<run-id>/` com SHA e metadados `scene=c01`, `shot_id=C01-P02`, `scene_mother_sha256` da mesma mãe; falhas bloqueiam o pacote, sem fallback. `workflow_run` do preview só cria vídeo se o artifact esperado existir. `draft_motion_heuristic_only=true` exige revisão de pivô/contato; testes de fixtures sintéticas não são arte aprovada.
