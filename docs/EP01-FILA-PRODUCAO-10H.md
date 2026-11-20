# EP01 — Campanha de 10 horas de trabalho planejado

**Repositório:** `HelioConde/VideoForge-IA` · **Canal:** `alchemy-lab` · **Episódio:** `mmorpg-conquiste-a-princesa-ep01`.

O objetivo é continuar a fila do EP01 durante **dez lotes independentes, cada um com 60 minutos de orçamento de trabalho**. São **600 minutos de capacidade planejada**, não uma promessa de duração exata em relógio: a execução pode terminar antes quando não houver tarefas seguras, ou ser interrompida por limites e falhas do GitHub.

A campanha não cria uma segunda fila paralela e **não reinicia tarefas**: dispara o controlador existente `ep01-image-animation-action-queue.yml`, que já contém 276 tarefas distribuídas entre 42 tomadas da continuidade V2, utiliza o ledger CAS `state/multi-agent-runtime` e registra os links das Actions filhas no painel [Issue #98](https://github.com/HelioConde/VideoForge-IA/issues/98).

## Dez lotes de execução

| Lote | Orçamento | Foco operacional |
|---|---:|---|
| 1 | 60 min | Conferir inventário, SHAs e próximos itens desbloqueados |
| 2 | 60 min | Continuar geração de camadas independentes válidas |
| 3 | 60 min | Avançar prévias de câmera por tomada |
| 4 | 60 min | Arquivar imagens e conferir comprovantes |
| 5 | 60 min | Prosseguir pela próxima prioridade real das 276 tarefas |
| 6 | 60 min | Continuar prévias e camadas permitidas |
| 7 | 60 min | Registrar continuidade e QA pendente |
| 8 | 60 min | Expandir cobertura de câmera das 42 tomadas |
| 9 | 60 min | Preparar materiais verificáveis para montagem parcial |
| 10 | 60 min | Consolidar resultados, bloqueios e próximas prioridades |

**Observação:** os focos representam intenção de trabalho, não tarefas falsamente concluídas. Em todos os lotes o controlador escolhe somente os próximos itens realmente disponíveis por ordem de prioridade e evidência SHA.

Por lote: até **2 imagens** (1 chamada paga por Action filha) e até **4 prévias de câmera**. Em dez lotes, capacidade de até **20 chamadas de imagens** e **40 prévias de câmera**. Não há garantia de que esse máximo será utilizado, nem autorização para repetir falhas com efeito externo incerto.

## Regras de qualidade

- Respeitar a continuidade C07/C08 V2 e preservar a versão MP4 de 42 tomadas já renderizada.
- Nunca gerar novamente mães e peças que já tenham arquivos válidos ou registros de falha incerta no ledger.
- Proibido voltar à separação de mãos e pegadas rejeitadas.
- Camadas RGBA só podem liberar rig se passarem QA real; **nenhuma animação articulada é aprovada automaticamente**.
- Identificar claramente prévias de câmera, imagens candidatas, animações e vídeos finais.
- Registrar run ID, SHA, duração observada, artifact, rejeições e bloqueios.
- Não publicar nem tornar público o EP01 no YouTube.
- Se um lote não entregar novas imagens ou prévias, encerrar os seguintes sem ocupar Actions à toa.
- Se um workflow falhar, interromper a campanha e preservar o ledger para revisão, sem tentar de novo uma chamada que pode ter sido cobrada.
- Os resultados por lote ficam em artifacts `ep01-10h-slot-N-<run>`; o sumário agrega exclusivamente os recibos verificados.

## Como acompanhar

1. [Campanha de 10 horas — GitHub Actions](https://github.com/HelioConde/VideoForge-IA/actions/workflows/ep01-10h-campaign.yml)
2. [Painel de produção do EP01 — Issue #98](https://github.com/HelioConde/VideoForge-IA/issues/98)
3. [Fonte do plano de dez lotes](../canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/FILA-PRODUCAO-10-HORAS.json)

Ao fim, haverá um artifact `ep01-campanha-10h-relatorio-<run>` com os números reais de lotes, imagens e prévias executados. Se algum estágio for bloqueado, o relatório será parcial e mostrará o bloqueio, sem alegar que as dez horas foram consumidas.
