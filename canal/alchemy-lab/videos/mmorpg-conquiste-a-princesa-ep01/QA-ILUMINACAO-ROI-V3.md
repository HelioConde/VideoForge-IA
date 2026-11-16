# QA de iluminação — máscaras V3

## 16/11/2026 — Separar alerta cromático de dúvida de iluminação

Correção em wardrobe_roi_color: divergência forte de histograma com lighting_differences_may_be_present verdadeiro, ausente ou inválido retorna EVIDENCIA_INSUFICIENTE, preservando métricas e chromatic_alert, sem reprovação automática nova. Só False booleano, após revisão externa, permite a reprovação cromática em ROIs verificadas. Nunca preencher esse campo apenas para obter resultado. Reprovações prévias do proprietário continuam ativas.

Regressão reproduzida: fixture sintética com mesma proporção RGB e exposição 10x menor era reprovada; após correção mantém incerteza. Controle vermelho versus preto com iluminação descartada continua reprovado. 23 testes ROI locais passaram. PNGs, polígonos V3 e contrato real não foram alterados: 0/8 máscaras semânticas e 0/4 pares, R2 bloqueada, nenhuma chamada paga. CI e integração pendentes nesta entrada; consultar registro mais recente antes de retomar. Próximo passo: revisar fontes e anotar diferenças de iluminação sem apagar a reprovação conhecida dos figurinos.

## 16/11/2026 — QA iluminação integrado (PR #64)

Commit [5285f51](https://github.com/HelioConde/VideoForge-IA/commit/5285f5150b73279fd26941373e31508b22f6977a) confirmado na main. Workflow [43944144582](https://github.com/HelioConde/VideoForge-IA/actions/runs/43944144582) SUCCESS: 23 testes ROI e recálculo das oito regiões sem escrever imagens. Fixtures de exposição testam o mecanismo, não aprovam os figurinos reais. Nenhuma máscara modificada nesta rodada; 0/8 aprovações semânticas e R2 bloqueada. Próximo passo: revisar as fontes completas, cobertura e iluminação; não definir flags de aprovação por histograma.

Verificação pós-merge: workflow semântico da main [43944320147](https://github.com/HelioConde/VideoForge-IA/actions/runs/43944320147) também terminou SUCCESS. Mantidos quatro pares reais sem evidência suficiente e nenhuma aprovação automática.
