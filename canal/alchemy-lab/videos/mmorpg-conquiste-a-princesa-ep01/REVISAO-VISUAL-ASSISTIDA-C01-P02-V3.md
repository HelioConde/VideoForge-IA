# C01-P02 — Inspeção visual assistida da comparação V3 (17/11/2026)

**Estado: CANDIDATA / NÃO APROVADA.** Esta é uma análise visual preliminar por assistente sobre a prancha real do repositório; **não é aceite do proprietário**, não altera `human_approval=false`, nem autoriza rig, MP4 ou publicação.

## Fontes verificadas
- [Comparação de seis painéis](QA-C01-P02-CONTATO-V3.jpg): fonte V1, edição de IA V3, patch localizado V3; respectivas ampliações.
- [Metadados de comparação](QA-C01-P02-CONTATO-V3.json): fonte SHA-256 `b055b93e2174625adb4b7f5eb4f5a40f88f9353bce0fe50e0ac193d6eb002a5e`; edição V3 `8b9d9acec8933e345b3099d536a1c410cf8da074d039fcbfd8eca2173ed4a84b`; patch V3 `17da28fcf733727a11d2d67a38a84611bd1192cff0e97d45d7db10169de9089d`.
- Execuções: [geração #44047381550](https://github.com/HelioConde/VideoForge-IA/actions/runs/44047381550) e [comparação #44047543396](https://github.com/HelioConde/VideoForge-IA/actions/runs/44047543396).

## Observações da inspeção visual
1. **Profundidade da bainha:** na versão V3, a bainha parece mais claramente externa/à frente do casaco. Isto ainda não certifica todo o contorno em cada camada RGBA.
2. **Luva inferior:** ela aparece à frente da bainha e parece apoiá-la, porém o fecho dos dedos, o ponto de aperto e a anatomia de contato precisam de revisão cuidadosa; sobreposição visual por si só não prova empunhadura funcional.
3. **Lâmina e bocal da bainha:** existe uma região estreita em que a lâmina deve ingressar exatamente pela abertura. A prancha não demonstra de forma inequívoca uma trajetória física contínua, largura compatível e oclusão correta no bocal. **Conferir em zoom antes de aprovar.**
4. **V3 completa vs. patch localizado:** as duas parecem próximas na área crítica; preservar ambas como candidatas. `exact_original_rgb_outside_roi=true` comprova apenas integridade fora da edição, não correção anatômica.
5. **Mão superior:** aparenta segurar o cabo; confirmar a continuidade dedo–punho–guarda e a ausência de peças duplicadas ao separar o personagem da espada.

## Bloqueio técnico adicional encontrado
O atual `videoforge/ep01_contact_gate.py` ainda compara quatro recortes, SHAs e diferença de recomposição com a **cena original V1 reprovada** (`EXPECTED_MOTHER_SHA=b055b93e...` e relatório RGB de 7,654/255). Por isso, o QA antigo não é evidência de que a V3 está pronta. **Não aprovar V3 usando o relatório/máscaras de V1.**

## Próximo procedimento obrigatório
1. Revisar lado a lado os closes da **edição V3 completa** e do **patch V3**, dando atenção ao bocal, à mão inferior e à bainha inteiramente fora da roupa. Não chamar de erro confirmado nem de correção aprovada antes da avaliação do responsável.
2. Se houver erro, editar apenas o contato anatômico em nova V4 versionada, preservando identidade, estilo, enquadramento, escala e restante do frame. Não usar translações arbitrárias ou a antiga bainha 981×1602.
3. Após escolha e aprovação da fonte, gerar de **uma única mãe escolhida** background limpo, corpo, bainha, espada, luvas e máscaras de oclusão no canvas nativo **941×1672**, com SHAs próprios.
4. Recalcular reconciliação por pixels e contato sobre essas novas camadas. Atualizar o gate para apontar aos novos SHAs, ao novo QA e a uma aprovação humana explícita daquela candidata; nunca reutilizar a aprovação/relatório do V1.
5. Só liberar rig articulado, movimento de câmera, MP4 e eventual publicação depois de contato, recomposição e autoria aprovados. O rig não deve deslocar o objeto inteiro para mascarar defeitos de origem.

**Decisão deste registro:** `assistant_preliminary_review=needs_closeup_review`; `human_approval=false`; `rig_ready=false`; `mp4_generated=false`; `youtube_uploaded=false`.
