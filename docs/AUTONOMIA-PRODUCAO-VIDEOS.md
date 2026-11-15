# VideoForge IA — Regra permanente de produção autônoma de vídeos (15/11/2026)

**Pedido do responsável:** ensinar o programa do GitHub a executar corretamente o ciclo de vídeos e animações, com o mínimo de orientação humana recorrente. Nossa função deve ser orientar objetivos, direção artística e aprovações finais, não consertar a mesma etapa manualmente toda vez. Metas: consistência de personagens, cinematografia, animação genuína por rig e malha, QA automático forte, persistência do aprendizado e melhoria contínua do próprio sistema.

## Máquina de estados e responsabilização

1. Ler o checkpoint mestre em `canal/<id>/videos/<video-id>/ESTADO-ATUAL.md`, `estado-atual.json`, histórico e assets reais na `main` **ANTES** de agir. Não duplicar desenhos, código, máscaras ou vídeos com SHA confirmado.
2. Usar roteirista/diretor para decidir evento, ângulo dramático, elenco e continuidade visual por tomada.
3. Artista gera imagem-mãe por perspectiva com a mesma identidade aprovada; arquivar original e SHA antes de anunciar conclusão. Número **total** de imagens sem máximo editorial, respeitando custo, segurança e autorização.
4. Separador de imagens cria background, máscaras RGBA, partes, cabelo, roupa, olhos e áreas ocultas. QA pixel a pixel sobre a arte-mãe, sem halos, duplicações ou deformação.
5. Animador rig Three.js + Remotion desenha pivôs, keyframes determinísticos, juntas, contatos e malha do cabelo/capa; NUNCA substituir por PNG inteiro ou zoom falso.
6. Renderer produz MP4 de prova, inspetor verifica quadros H.264, silhuetas, movimento localizado, áudio e continuidade. Qualquer falha técnica diagnóstica deve gerar ação corretiva identificada e reteste **do componente afetado**, não reconstrução integral.
7. Registrar todo avanço real e diagnóstico no arquivo mestre e histórico na `main` (paths, SHA, commit, run, erros, resultado e próxima ação); escolher a próxima etapa pendente pelo estado, não por suposição do chat.
8. O programa deve aprender **padrões de correção** de erros repetidos: registrar causa, solução, teste de regressão e regra nova para impedir reincidência. Não considerar "correção" apenas relançar o mesmo job. Depois de repetidas falhas não determinísticas, suspender etapa e escalar com evidências.
9. **Nunca** afirmar autonomia completa, aprovação artística, geração de mídia, publicação ou custo consentido sem evidência. Aprovação humana de identidade e publicação permanecem controles deliberados.

## Implementação inicial efetiva do EP01

### Integração do seletor V2 ao programa de geração

O `videoforge/cinematic_direction.py` detecta o remake ativo pelo `estado-atual.json`, valida o manifesto de tomadas do remake e envia plano, elenco, emoção, câmera e direção dramática ao `production_scenes.py`. O seletor histórico V1 foi mantido para diagnósticos antigos. `production_scenes.generate_scene` exige identidade com PNG de âncora aprovado por SHA, além das verificações de custo do `image_generation_policy.py`. Regressões: `tests/test_remake_cinematic_integration.py`. **A montagem automática de camadas/rig e render de todas as cenas ainda não foi integrada.**

- Coordenador: `videoforge/remake_autopilot.py` lê o plano e a evidência por SHA; decide próximo estágio sem chamar modelo, com relatório estruturado e sincronização idempotente do checkpoint/histórico.
- Política de gasto e execução: `canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/autonomy-policy.json`. Atualmente geração automática paga está **desativada** até autorização separada; isso não é limite total editorial de imagens.
- Workflow: `.github/workflows/remake-autonomy.yml` roda testes, diagnóstico e atualização do checkpoint diariamente ou manualmente, sem IA e sem publicar. Não confundir com executor completo: ainda é necessário implementar despacho seguro/idempotente, encadeamento de workflows de geração/rig e reparos reais.
- Geradores e rigs **já existentes** devem ser reutilizados, nunca substituídos por pipeline novo só para fingir automação: `production-art-by-request.yml`, `production-scene-by-request.yml`, `production-scene-mother-layers.yml`, `directed-rig-preview.yml`, `videoforge/directed_rig.py` e validadores QA.

## Critérios de evolução

**Etapa atual:** coordenador de preflight e retomada. **Próximas etapas de software:** (1) despacho idempotente com ledger por imagem/SHA e controles de orçamento, (2) encadeamento de geração e isolamento de camadas, (3) criação de rig e correção de falhas determinísticas, (4) QA audiovisual e montagem final. Não ativar gastos nem publicações automaticamente ao implementar novas funções.

Objetivo final: o usuário apenas descreve um vídeo e fornece feedback artístico; o VideoForge pesquisa quando apropriado, cria, anima, testa, registra e entrega mídia verificável no GitHub, com supervisão concentrada nas decisões realmente subjetivas.
