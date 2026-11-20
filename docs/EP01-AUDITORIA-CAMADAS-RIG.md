# EP01 — auditoria de prontidão para rig (QA técnico, sem IA)

Esta etapa complementa a fila de produção de 10 lotes sem modificá-la nem consumir imagens.

**Fonte de verdade:** 42 tomadas do plano de câmera `continuity-v2`, 4.890 frames. Para cada tomada, conferir por SHA a imagem-mãe e as peças independentes já arquivadas; registrar também as ausentes ou rejeitadas.

A auditoria realiza quatro classes de verificação: proveniência, SHA256, dimensões/posicionamento de canvas e presença de transparência RGBA em personagem/objeto. Registrar a natureza da divergência (ex.: peça nativa 941×1671 contra mãe 941×1672, sem redimensionar pixels). **Passar geometricamente não significa boa anatomia, figurino, contato ou recomposição**.

C01-P02 e C01-P04 continuam bloqueadas para reuso de partes antigas rejeitadas ou mãos independentes. C07/C08 devem usar plano específico V2, não camadas do plano de 40 tomadas sem nova revisão.

A Action [EP01 — auditoria de camadas RGBA](https://github.com/HelioConde/VideoForge-IA/actions/workflows/ep01-rig-readiness-audit.yml) gera dois arquivos: `EP01-rig-readiness.json` e `EP01-rig-readiness.md`, com status técnico por tomada e links de origem nos manifests.

Regras: sem proxy, sem chamadas pagas, sem render de vídeo, sem manipulação de PNG, sem habilitar rig ou publicar no YouTube. Nenhuma aprovação humana é inferida automaticamente.

**Próximo passo após o QA:** separar as tomadas cuja origem é íntegra e que possuem todas as peças, corrigir alinhamento e recomposição sem alterar a arte, e selecionar um piloto de rig após revisão visual independente.