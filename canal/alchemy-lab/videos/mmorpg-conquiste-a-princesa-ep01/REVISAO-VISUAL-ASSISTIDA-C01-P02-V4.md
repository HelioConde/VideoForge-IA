# C01-P02 — Revisão visual assistida V4 (17/11/2026)

**Status: duas candidatas V4 geradas, comparação técnica concluída, nenhum contato aprovado.** Inspeção por assistente é preliminar e **não substitui revisão do proprietário**.

## Evidências
- [Comparação V1, V3, V4 completo e V4 localizado](QA-C01-P02-CONTATO-V4.jpg), com closes de contato.
- [Relatório QA](QA-C01-P02-CONTATO-V4.json).
- Geração V4: [run 44063304090](https://github.com/HelioConde/VideoForge-IA/actions/runs/44063304090), **success**.
- Comparação V4: [run 44063462507](https://github.com/HelioConde/VideoForge-IA/actions/runs/44063462507), **success**.
- A primeira tentativa V4 [44063003598](https://github.com/HelioConde/VideoForge-IA/actions/runs/44063003598) parou em HTTP 400 e **não gerou PNG**; diagnóstico sanitizado posteriormente acrescentado ao proxy, sem divulgar corpo do erro/credenciais.

## Fontes e versões (cópias permanentes)
| Papel | SHA-256 | Estado |
|---|---|---|
| Mãe V1 histórica | `b055b93e2174625adb4b7f5eb4f5a40f88f9353bce0fe50e0ac193d6eb002a5e` | Contato rejeitado |
| Patch local V3, fonte do reparo | `17da28fcf733727a11d2d67a38a84611bd1192cff0e97d45d7db10169de9089d` | Candidata não aprovada |
| V4 edição completa | `078ba6c72bd8cba74d5a28f12948b94f06c8c348a5c291438820ee7f7e9c2c14` | Candidata não aprovada |
| V4 patch localizado | `3a3d96e9328426c857b1e40d43d0c4edfbe79f07ef9d43c86ef63f6c57f919a9` | Candidata não aprovada |

Todos os V4 têm **941×1672**. O patch V4 mantém **todos os pixels fora da ROI (370,790,900,1660)** exatamente como a fonte V3; MAE RGB contra V3 de **3,0983/255** é métrica de modificação, **não de anatomia ou qualidade**.

## Inspeção visual preliminar
- A V4 apresenta a lâmina com entrada **aparentemente mais explícita** no bocal da bainha; ainda é necessário confirmar a continuidade da lâmina e a correta ocultação do trecho embainhado.
- A luva inferior parece segurar a bainha pelo lado de fora do casaco. Verificar em resolução nativa a posição dos dedos e contato com a superfície, sem atribuir aprovação automática.
- **Ponto de atenção novo:** o bocal dourado e seus arabescos foram simplificados/reconfigurados em V4 em comparação com V3. A posição do detalhe vermelho e o formato do aro mudaram. **Pode violar a continuidade do objeto canônico da Bíblia Visual; não promover V4 sem comparação com mestre aprovado.**
- O punho superior segurando o cabo parece preservado, mas ainda requer separação RGBA e QA de recorte antes de qualquer animação.
- Não tratar a V4 completa e o patch como imagens idênticas. A V4 localizada preserva a cena fora da região de edição, sendo a candidata mais conservadora para revisão, não automaticamente a melhor em anatomia.

## Gates e próximos passos
1. Comparar o desenho do bocal da V4 com a bainha mestre da Bíblia Visual. Se o ornamento descaracterizou o objeto, marcar reprovado ou solicitar reparo mais conservador; manter V3.
2. Aguardar decisão visual do proprietário sobre a tomada/objeto. Não inferir aceitação com base em **Actions success**, SHA ou MAE.
3. Após escolher e aprovar UMA fonte, extrair de novo cenário sem objetos, corpo, bainha, espada, luvas e máscaras RGBA desta mesma fonte. O gate antigo está atrelado à V1 reprovada e **não certifica V4**.
4. QA do encontro lâmina/bocal, profundidade da bainha, dedos, recomposição RGB e limite de câmera/rig. Só então planejar/articular o rig, gerar MP4 e avaliar publicação.
5. Outras imagens-mãe independentes do episódio podem continuar em fila com a Bíblia Visual, sem transformar C01-P02 em aprovada.

**Decisões de estado:** `image_generated=true`; `technical_archive_qa=true`; `visual_candidate_only=true`; `human_approval=false`; `rig_ready=false`; `mp4_generated=false`; `youtube_uploaded=false`.
