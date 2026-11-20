# EP01 — QA de camadas RGBA e prontidão para rig — 20/11/2026

A campanha de prévias da continuidade V2 chegou a **42/42 tomadas com câmera**, conforme o ledger da fila. Isso é **câmera sobre imagens existentes**, e não rig, dublagem ou animação articulada.

A auditoria read-only [Action #44670895298](https://github.com/HelioConde/VideoForge-IA/actions/runs/44670895298) foi concluída com sucesso na `main`. [Baixar relatório por tomada](https://github.com/HelioConde/VideoForge-IA/actions/runs/44670895298/artifacts/14599359892) (JSON e Markdown), gerado pelo código `scripts/ep01_rig_readiness_audit.py`, incluído via [PR #116](https://github.com/HelioConde/VideoForge-IA/pull/116).

## Inventário verificado

| Classificação técnica | Quantidade de solicitações de peças |
|---|---:|
| Peças ausentes na verificação por SHA | 106 |
| Candidatas arquivadas rejeitadas tecnicamente | 10 |
| Peças com SHA/proveniência e geometria de canvas verificadas | 9 |
| Peças exigindo QA de alinhamento/canvas/origem | 21 |
| **Total do plano de peças** | **146** |

**Importante:** o total de 10 rejeições representa as peças rejeitadas identificadas em todo o histórico do plano, não somente as rejeições ocorridas na campanha de 10 horas. A contagem é um instantâneo da Action; novas gerações podem alterá-la.

O diagnóstico mostra que vários PNGs do modelo usam **941×1671** enquanto a imagem-mãe correspondente usa **941×1672**: não mover, escalar, recortar nem fingir que os pixels já estão alinhados; usar somente soluções de registro aprovadas com SHA e QA posterior. Uma candidata geometricamente íntegra não prova que as mãos, anatomia, figurino, carrinho ou recomposição estão visualmente corretos.

## Restrições e próximos passos

- **0/42 rigs animados aprovados**; o auditor não modifica PNGs, não chama proxy e não concede aprovação.
- C01-P02 e C01-P04 exigem respeito às rejeições/à política de mãos independentes; C07 e C08 exigem peças próprias da continuidade V2, nunca reutilizar um plano antigo apenas porque o ID coincide.
- Priorizar completar camadas faltantes com a fila existente e revisar as 21 peças com QA técnico pendente, sem cobrar novamente uma rejeição arquivada.
- Para liberar um rig: integrar camadas independentes com fundo reconstruído, conferir recomposição visual e contatos sob movimento, validar pivôs e QA temporal; então obter aprovação do criador.
- Manter o MP4 único de 42 tomadas como **prévia para revisão**, não como episódio pronto. Não publicar no YouTube.

A fonte auditável dos números é o artifact da Action; [painel da fila](https://github.com/HelioConde/VideoForge-IA/issues/98) tem o progresso por tomada.
