# EP01 V3 — auditoria da fragmentação das máscaras arquivadas

**Data:** 16/11/2026. **Run de leitura:** [43951026350](https://github.com/HelioConde/VideoForge-IA/actions/runs/43951026350) (SUCCESS; 7 testes). **Implementação:** `videoforge/wardrobe_roi_fragmentation.py`, `tests/test_wardrobe_roi_fragmentation.py`, `qa-wardrobe-roi-fragmentation.yml`.

A auditoria lê os oito PNGs RGBA V3 do repositório e valida SHA, RGB e alfa com a auditoria anterior. Usa conectividade de oito vizinhos, em pixels da fonte, sem escalonamento, inpainting, mudanças de arte ou geração paga. O JSON completo é um artifact temporário `roi-v3-fragmentation` da Action. Números abaixo conferidos diretamente nos logs da execução.

| Personagem | Região | Pose | Pixels selecionados | Componentes | Maior componente | Ilhas menores que 5 px |
|---|---|---|---:|---:|---:|---:|
| Aldric | barba | A | 378 | 6 | 96,56% | 4 |
| Aldric | barba | B | 806 | 2 | 95,41% | 0 |
| Aldric | tecido_externo | A | 5604 | 20 | 57,17% | 11 |
| Aldric | tecido_externo | B | 7445 | 23 | 68,80% | 15 |
| Aldric | painel_central | A | 4004 | 57 | 68,08% | 41 |
| Aldric | painel_central | B | 3596 | 225 | 14,63% | 163 |
| Elara | corpete_roxo_palacio | A | 17102 | 36 | 69,64% | 19 |
| Elara | corpete_roxo_palacio | B | 587 | 10 | 93,19% | 8 |

## Prioridade decorrente

1. **Aldric / painel central / B:** 225 componentes para 3.596 pixels; maior componente só 14,63%. É o maior sinal de fragmentação. Examinar os originais com o [recorte nativo 1x](assets/qa-roi-review-native-v3/aldric-painel_central-b-CONTEXTO-1X.png) e diferenciar tecido de brocados. O filtro HSV pode estar capturando apenas fios e ornamentos, não o tecido contínuo.
2. **Aldric / painel central / A:** 57 componentes; inspecionar o [recorte 1x](assets/qa-roi-review-native-v3/aldric-painel_central-a-CONTEXTO-1X.png) antes de comparar com B.
3. **Aldric / tecido externo A/B:** 20 e 23 componentes; acompanhar lança e sombras nos [recortes nativos](REVISAR-ROI-NATIVA-V3.md).
4. **Elara / corpete A/B:** 36 e 10 componentes; a cobertura da versão B continua muito menor. Verificar oclusão antes de falar em inconsistência do vestido.
5. **Aldric / barba A/B:** 6 e 2 componentes, mas conectividade alta **não** significa barba correta; verificar boca, pele e bigode.

**Inspeção visual adicional do PNG 1x:** o painel central B original contém tecido bordô amplo ao redor dos bordados; a máscara seleciona principalmente traços finos verticais e omite grandes superfícies do tecido. A cobertura da máscara atual é **inadequada para inferir continuidade da cor do painel**. A anotação `REVISAO-SEMANTICA-ROI-V3.json` marcou a candidata como evidência insuficiente, sem aprovar/reprovar o figurino automaticamente. Reanotar preferencialmente em regiões separadas de torso e saia, preservando cinto e manto como exclusões.

**Não fazer preenchimento morfológico indiscriminado**: ele poderia criar tecido falso e borrar detalhes válidos. Priorizar revisão visual da fonte original e anotações de máscara semântica independentes dos classificadores de cor.

**Estado oficial inalterado:** oito máscaras técnicas candidatas e 0/8 máscaras semanticamente validadas, quatro pares canônicos pendentes, reprovações de Aldric/Elara ativas, R2/MP4/YouTube bloqueados, nenhuma nova imagem paga.
