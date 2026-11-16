# EP01 V3 — conferência visual em pixels nativos (sem interpolação)

**Esta é uma área de revisão, não um certificado de fidelidade visual.** Todas as pranchas são derivadas de PNGs já arquivados com SHA; os quatro painéis de cada arquivo (fonte, antes, pixels removidos, depois) conservam resolução 1:1 por área da fonte. Não existe geração de IA ou render MP4 nesta etapa.

[Relatório de oito pranchas e hashes](QA-ROI-REVISAO-NATIVA-V3.json) | [Revisão semântica ainda pendente](REVISAO-SEMANTICA-ROI-V3.json) | [Relatório V3 de exclusões](QA-ROI-EXCLUSOES-V3.json)

| Personagem e região | Fonte A / pose ou câmera 1 | Fonte B / pose ou câmera 2 |
|---|---|---|
| Aldric — barba | [Abrir original + antes/depois](assets/qa-roi-review-native-v3/aldric-barba-a-CONTEXTO-1X.png) | [Abrir original + antes/depois](assets/qa-roi-review-native-v3/aldric-barba-b-CONTEXTO-1X.png) |
| Aldric — tecido externo | [Abrir original + antes/depois](assets/qa-roi-review-native-v3/aldric-tecido_externo-a-CONTEXTO-1X.png) | [Abrir original + antes/depois](assets/qa-roi-review-native-v3/aldric-tecido_externo-b-CONTEXTO-1X.png) |
| Aldric — painel central | [Abrir original + antes/depois](assets/qa-roi-review-native-v3/aldric-painel_central-a-CONTEXTO-1X.png) | [Abrir original + antes/depois](assets/qa-roi-review-native-v3/aldric-painel_central-b-CONTEXTO-1X.png) |
| Elara — corpete roxo palaciano | [Abrir original + antes/depois](assets/qa-roi-review-native-v3/elara-corpete_roxo_palacio-a-CONTEXTO-1X.png) | [Abrir original + antes/depois](assets/qa-roi-review-native-v3/elara-corpete_roxo_palacio-b-CONTEXTO-1X.png) |

## O que verificar

1. **Barba de Aldric:** conferir bigode, interior da boca, pele do queixo, gola e pelos reais. O personagem está com boca aberta na candidata B, o que afeta o contorno da região.
2. **Manto de Aldric:** confirmar onde a haste da lança atravessa o tecido, sem apagar dobras verdadeiras.
3. **Painel central:** separar tecido bordô dos detalhes dourados e do cinto, em ambas as poses.
4. **Corpete de Elara:** identificar apenas os pixels visíveis do painel roxo. No enquadramento B, oclusões e joias não devem ser resolvidas inventando pixels ocultos.

As imagens servem para anotar o que falta; nenhum SHA ou métrica de pixels transforma essas máscaras em arte canônica.

## Situação e critérios de saída

- Oito pranchas PNG 1:1 publicadas e verificadas pelo workflow [43949781156](https://github.com/HelioConde/VideoForge-IA/actions/runs/43949781156).
- Oito máscaras candidatas V3 continuam sem confirmação semântica; quatro pares oficiais permanecem pendentes.
- R2, vídeo oficial e upload bloqueados; preservar reprovações conhecidas de Aldric e Elara.
- Após revisão das imagens em resolução nativa, registrar evidências em `REVISAO-SEMANTICA-ROI-V3.json`. Não alterar flags de aprovação sem análise visual comprovada.

