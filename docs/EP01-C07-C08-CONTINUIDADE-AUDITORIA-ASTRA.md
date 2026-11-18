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

## QA preliminar da prévia MP4 (amostragem de 27 frames)

**Fonte efetivamente examinada:** [Actions #44266014731 — MP4 V2 de 42 tomadas](https://github.com/HelioConde/VideoForge-IA/actions/runs/44266014731), artifact `EP01-42-tomadas-MP4-continuidade-V2-44266014731`. Arquivo `EP01-continuidade-V2-42-tomadas.mp4`, SHA-256 `6ca502f74e024414dc452ce3d05c643d17ddb108995401853ecdc57ecf439048`. Verificados H.264, **540×960, 30 fps, 4.890 frames, 163 s**. O arquivo de QA original declara **sem rig, sem áudio, sem aprovação humana**. Nenhuma inferência nova foi feita.

**Escopo da inspeção:** amostragem visual de um frame perto do início, meio e fim de **cada uma das nove tomadas** (27 frames no total), não análise quadro a quadro do movimento. Trecho do vídeo: **69–98 s (1:09–1:38)**. [Planilha JSON de achados por tomada](../canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/QA-C07-C08-PREVIA-MP4-V2-AMOSTRAGEM.json).

**Fontes dos PNGs corretamente verificadas:** [Actions #44390366374](https://github.com/HelioConde/VideoForge-IA/actions/runs/44390366374), artifact `ep01-c07-c08-contact-qa-44390366374`. São **nove imagens distintas usadas nas nove tomadas:** 7 mães V2, C07-P01 original e C07-P04 reutilizando **a mãe ORIGINAL C07-P03**. A mãe original não é a mãe V2 de C07-P03. O código `videoforge/ep01_continuity_v2.py` (função `revised_camera_plan`) confirma esta seleção — portanto **C07-P04 possui composição separada para o diálogo no MP4** e não deve ser regenerada apenas por ser uma reutilização. O primeiro contato de QA que referenciava a mãe V2 para C07-P04 foi corrigido no gerador de prancha.

### Achados da prévia (ainda sem aprovação visual)

| Tomada | Tempo | Observação de QA | Prioridade |
|---|---|---|---|
| C07-P01 | 1:09–1:12 | A fuga parece vir na direção da câmera/diagonal esquerda; o sentido `screen_right` não fica inequívoco | Média |
| C07-P02 | 1:12–1:15 | Dois mascarados, sem Elara, conforme o elenco previsto; direção lateral da perseguição ainda ambígua | Baixa |
| C07-P03 | 1:15–1:18 | Elara aparece em movimento para a esquerda do quadro, com Kael parado à direita; o encontro visual não é convincente | **Alta** |
| C07-P04 | 1:18–1:22 | Composição distinta mostrando Elara e Kael em conversa, extraída da mãe original C07-P03; preservar | Baixa |
| C08-P01 | 1:22–1:25 | Elara fica ao outro lado/atrás do carrinho; conferir clareza de profundidade e proteção por Kael | Média |
| C08-P02 | 1:25–1:29,33 | Kael empurra sozinho, mas ainda não há movimento articulado do giro; fonte PNG de **1053×1493** exige revisão de crop 9:16 | **Alta** |
| C08-P03 | 1:29,33–1:33 | Dois perseguidores do lado oposto, Kael no seguro; barricada já está montada após corte, sem giro animado | **Alta** |
| C08-P04 | 1:33–1:36 | Elara se desloca à direita; verificar se o bloqueio dos perseguidores pela carroça fica espacialmente legível | Média |
| C08-P05 | 1:36–1:38 | Kael reencontra Elara; fonte PNG de **1054×1493** requer conferir crop e personagem à borda direita | Média |

**Observação de proporção:** C08-P02 e C08-P05 continuam sendo **imagens verticais**, porém de proporção mais larga que o enquadramento final 9:16; a montagem pode cortar elementos laterais. Não confundir padding da prancha de contato com tarjas existentes no MP4.

### Correções recomendadas, sem executar geração

1. **Agente 03 + Agente 09:** revisar blocking/eixo entre C07-P01, C07-P02 e **C07-P03**. Exigir encontro compreensível de Elara chegando a Kael, não corrida em direção contrária. Priorizar reposicionamento/câmera/continuidade; gerar mãe nova apenas se as fontes não permitirem resolver.
2. **Agente 07 + Agente 08:** planejar rig e animação física da carroça entre **C08-P02 e C08-P03** (pivôs, mãos conectadas, rodas no solo e trajetória do giro), em vez de sugerir movimento apenas com zoom/corte. Validar mesmo carrinho e mesma posição final.
3. **Agente 09 + Agente 12:** rever C08-P04 para a barricada impedir realmente os perseguidores. Auditar crop 9:16 e limites de C08-P02/C08-P05 sem cortar mãos, figurino e ações.
4. **Agente 12:** só aprovar após assistir ao trecho completo e inspecionar frames intermediários, rigs, áudio e identidade. Esta inspeção por amostragem não valida movimento entre todos os frames.

**Estado da produção permanece intacto:** nenhum PNG aprovado foi substituído, nenhum rig ou novo MP4 de produção foi executado, nenhuma chamada de IA e nenhum upload. A auditoria histórica do Astra segue `blocked` até sua consolidação verificável. O vídeo examinado é **prévia técnica**, não episódio final.
