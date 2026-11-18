# EP01 C07/C08 — Auditoria Astra de continuidade (evidência documental)

**Estado:** sete achados **sustentados documentalmente**, revisão visual **pendente**; consolidação final do Agente 01 **não aprovada**. **Não usar este documento para autorizar imagens, renders, substituição de assets ou upload.**

- Fonte fixada: `canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/CONTINUIDADE-C07-C08-V2.json`, SHA-256 de conteúdo `890b65a477fe88c5d7e790afc7291b9fd3f063c35859d4c5bfab932115ba7468`.
- Verificação reexecutada sem inferência: [GitHub Actions #44380156316](https://github.com/HelioConde/VideoForge-IA/actions/runs/44380156316). Artifact `c07-c08-documentary-qa-44380156316`, com as evidências e JSON Pointers por faceta.
- Auditoria Astra original: [GitHub Actions #44359549902](https://github.com/HelioConde/VideoForge-IA/actions/runs/44359549902), modelo `gpt-6-astra`, **4 respostas** (01 → 03 → 12 → 01), **31.134 tokens de entrada + 7.201 de saída = 38.335**; custo USD não informado pelo proxy.
- Estado histórico (sem sobrescrever): [`runtime/c07-c08-astra-v1.json`](https://github.com/HelioConde/VideoForge-IA/blob/state/multi-agent-runtime/runtime/c07-c08-astra-v1.json), checkpoint de **bloqueio documental** SHA-256 `e83293081ca59ced280dcc2a383cc1e0e263aa9cd65bda40de9370716dbc7606`.
- A última resposta Astra tem `response_id`, tokens e hash, mas **não foi salva em texto**. O motivo exato de sua rejeição não pode ser reconstruído. O Agente 12 apoiou sete achados no manifesto; isto não constitui validação das imagens existentes.
- Reexecutar a auditoria inteira não é uma solução de recuperação: **não repetir automaticamente chamadas com cobrança ou resultado incerto**.

## Tomadas previstas na revisão C07/C08

| Tomada | Frames [início, fim exclusivo) | Acontecimento documentado |
|---|---|---|
| C07-P01 | 2070–2160 | Elara foge sozinha |
| C07-P02 | 2160–2250 | Perseguidores atrás de Elara |
| C07-P03 | 2250–2340 | Elara encontra Kael perto do carrinho |
| C07-P04 | 2340–2460 | Elara pede ajuda; Kael responde |
| C08-P01 | 2460–2550 | Kael percebe o carrinho |
| C08-P02 | 2550–2680 | Kael empurra e gira o carrinho sozinho |
| C08-P03 | 2680–2790 | Barricada separa Kael dos perseguidores |
| C08-P04 | 2790–2880 | Elara escapa pela passagem lateral |
| C08-P05 | 2880–2940 | Kael alcança Elara além da barricada |

O script `orchestrator/continuity_evidence.py` valida que os intervalos acima não tenham lacunas, sobreposição ou IDs duplicados. Isso **não** significa que o MP4 renderizado esteja conforme esses frames.

## Sete achados revisados pelo Agente 12

Abaixo estão as **prescrições do manifesto**, não observações sobre imagens. O Agente 12 marcou todas como `supported` em relação ao texto-fonte.

| Aspecto | Evidência documental | Checagem necessária nas imagens ou no MP4 |
|---|---|---|
| Direção de fuga | `/rules/screen_flee_direction`: `left_to_right` | Elara mantém movimento de esquerda para direita em tomadas consecutivas, sem teletransporte |
| Posições relativas | Prompts de `/shots/4` e `/shots/6` | Elara passa para trás de Kael, segue pela passagem; Kael não muda de lado sem movimento |
| Perseguidores | `/rules/pursuers_origin`, prompts de `/shots/1` e `/shots/6` | Exatamente dois mascarados a perseguem pela esquerda; não ajudam Kael nem tocam o carrinho |
| Carrinho | `/rules/cart_initial`, `/rules/cart_action`, `/rules/cart_final` | O **mesmo carrinho**, inicialmente junto à parede direita, é empurrado **só por Kael**, girado e torna-se barricada perpendicular |
| Ordem das tomadas | `/shots/0/start_frame` e `/shots/8/end_exclusive` | Conferir edição real de C07-P01 a C08-P05, inclusive entradas e saídas |
| Coerência narrativa | `/creator_feedback`, beats de `/shots/2`, `/shots/3`, `/shots/8` | Mostrar encontro → pedido de ajuda → intervenção → reencontro, sem fundir tempos distintos numa imagem |
| Pontes de transição | `/editorial_v2/adds`: `C07-P04`, `C08-P05` | As duas novas tomadas precisam existir visualmente e ligar as posições anteriores e posteriores |

A auditoria completa, inclusive declarações e recomendações originais do Agente 03, justificativas do Agente 12, IDs de findings e hashes por JSON Pointer, está no artifact do workflow.

## Próxima etapa autorizável

1. **QA visual independente:** comparar cada imagem-mãe e a montagem das nove tomadas com este plano; informar IDs e frames dos defeitos sem regenerar automaticamente.
2. **Correção dirigida:** criar proposta para apenas as tomadas com erros concretos, respeitando Bíblia Visual, camadas, rigs e versões já aprovadas; exigir autorização antes de alterar produção ou consumir inferência.
3. **Consolidação:** após evidência verificável do Diretor Geral e revisão independente, registrar decisão nova e separada. Não reclassificar o checkpoint histórico `blocked` como `completed` sem comprovação.

### Proteções

- Nenhuma imagem foi gerada por esta auditoria.
- Nenhum frame foi inspecionado automaticamente neste teste documental.
- Nenhuma alteração em cenas ou publicação foi realizada.
- O estado `blocked` continua correto para a auditoria original.
- O relatório é reprodutível por `python -m orchestrator.continuity_evidence --github-state --output <arquivo.json>` com acesso somente leitura à branch de estado.
