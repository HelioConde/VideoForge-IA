# Revisão das máscaras candidatas V4


## 16/11/2026 — V4: resíduos de gola na barba sentada

A candidata V4 amplia a faixa inferior de exclusão de Aldric A para x=496..557 e y=339..359 na fonte SHA original; protege explicitamente y=308..335. Remove 4 pixels adicionais em relação à V3 (15 no total contra a máscara refinada inicial, 374 retidos). Todos os pixels acima de y=339 permanecem idênticos à V3. As outras sete máscaras mantêm seus hashes. V2/V3 e fontes preservadas.

26 testes ROI locais passaram, incluindo regressão da faixa inferior e hashes das sete regiões não alteradas. QA-ROI-CONTEXTO-V4.jpg e QA-ROI-EXCLUSOES-V4.json são candidatas; 0 aprovações semânticas, 0/4 pares oficiais, R2/MP4/YouTube bloqueados. CI/publicação V4 pendentes neste registro. Não ampliar Elara B ou excluir boca/bigode de Aldric B sem delimitação confiável.

Fontes e versões anteriores: [V3](REVISAR-MASCARAS-FILTRADAS-V3.md). [Prancha contextual](QA-ROI-CONTEXTO-V4.jpg).
