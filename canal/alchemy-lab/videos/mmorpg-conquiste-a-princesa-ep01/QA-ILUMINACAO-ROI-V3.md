# QA de iluminação — máscaras V3

## 16/11/2026 — Separar alerta cromático de dúvida de iluminação

Correção em wardrobe_roi_color: divergência forte de histograma com lighting_differences_may_be_present verdadeiro, ausente ou inválido retorna EVIDENCIA_INSUFICIENTE, preservando métricas e chromatic_alert, sem reprovação automática nova. Só False booleano, após revisão externa, permite a reprovação cromática em ROIs verificadas. Nunca preencher esse campo apenas para obter resultado. Reprovações prévias do proprietário continuam ativas.

Regressão reproduzida: fixture sintética com mesma proporção RGB e exposição 10x menor era reprovada; após correção mantém incerteza. Controle vermelho versus preto com iluminação descartada continua reprovado. 23 testes ROI locais passaram. PNGs, polígonos V3 e contrato real não foram alterados: 0/8 máscaras semânticas e 0/4 pares, R2 bloqueada, nenhuma chamada paga. CI e integração pendentes nesta entrada; consultar registro mais recente antes de retomar. Próximo passo: revisar fontes e anotar diferenças de iluminação sem apagar a reprovação conhecida dos figurinos.
