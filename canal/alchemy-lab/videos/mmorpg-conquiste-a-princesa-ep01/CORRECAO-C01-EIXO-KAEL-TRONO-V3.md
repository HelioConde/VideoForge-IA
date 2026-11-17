# Dorama EP01 — correção de direção Kael → Trono (C01-P03 / C01-P04)

**Decisão do criador, 17/11/2026:** Kael ajoelhado deve estar **virado PARA o trono/rei Aldric**, não de costas para a autoridade. A câmera pode captar parte do rosto em três quartos, mas o eixo do corpo (peito, quadril, joelhos, cabeça e olhar) precisa apontar fisicamente para o rei no topo da escadaria. Não basta virar a cabeça mantendo o corpo apontado para outro lado.

## Escopo de cenas

- **C01-P03 / nova mãe V3:** Kael ajoelhado em primeiro plano; Aldric **de pé** diante do trono, distante; **sem guardas, lanças ou espada** nesta tomada. Câmera baixa de três quartos revelando perfil sem inverter o eixo corpo → trono.
- **C01-P04 / nova mãe V3:** Kael ajoelhado em direção ao trono; Aldric **sentado**; exatamente dois guardas nas laterais, cada um segurando **sua própria lança pelo terço inferior/base**, com dedos e polegar fechados em contato real com a haste. Pontas formando X **alto**, atrás de Kael. Escala e anatomia coerentes.
- **C01-P04-ALT / variante:** mesma ação/elenco, câmera um pouco mais baixa ou lateral para comparação de expressões, **sem trocar a orientação de Kael**.

## Regras de identidade e geração

1. Usar como referência as **imagens V2 originais arquivadas no GitHub** e as referências da Bíblia Visual, com SHA validado, sem copiar poses incompatíveis. Preservar estilo anime/manhwa fantasia 2D semirrealista, figurino, trono e arquitetura, luz dourada e vitrais roxos.
2. Gerar nova imagem-mãe pelo **Codex Proxy no GitHub**. Não substituir nem apagar V1/V2; arquivar V3 em `assets/geracoes/production-scene-mother-orientation-v3/<run_id>/`, com PNG, `.production.json`, manifesto e SHA.
3. As imagens V3 feitas no GitHub são **novos resultados do proxy**, não cópias byte a byte das prévias feitas nesta conversa. Confrontar visualmente as novas versões com o objetivo e referências.
4. O resultado da geração e o SHA comprovam **proveniência técnica**, não correção anatômica ou aprovação humana. QA manual obrigatória: direção do olhar, eixo corporal, mãos, dedos, lanças, roupas, chão e coerência de câmera.
5. **Nenhuma V3 será promovida automaticamente a imagem principal/rig.** Após escolher visualmente a mãe, gerar novas imagens independentes de fundo, personagens, objetos e partes móveis com RGBA pelo proxy, sem recortar pixels da mãe.
6. `human_visual_approval=false`, `rig_ready=false`, `mp4_generated=false`, `youtube_uploaded=false`.

**Mecanismo:** `videoforge/ep01_throne_orientation_v3.py`, workflow `.github/workflows/ep01-throne-orientation-v3.yml`, pedido `PEDIDO-CORRECAO-ORIENTACAO-V3.json`.
