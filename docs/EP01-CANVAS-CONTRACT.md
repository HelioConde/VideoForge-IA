# EP01 — contrato de canvas antes da geração

Atualizado em 24/11/2026. Escopo: `ep01_proxy_separate_parts`, fila de peças e workflow de peça individual.

## Defeito e correção

O prompt exigia o canvas nativo da mãe (por exemplo, 941×1672), mas o payload sempre solicitava `1024x1536`. Agora o pedido usa exatamente `WIDTHxHEIGHT` da fonte, somente quando permitido pelo contrato documentado de `gpt-image-2`: dimensões inteiras positivas e múltiplas de 16, maior lado até 3840, proporção até 3:1 e área entre 655360 e 8294400 pixels.

Fontes como 941×1672 e 1053×1493 não atendem esse contrato. O erro `EP01_PROXY_PARTS_UNSUPPORTED_NATIVE_CANVAS` interrompe o preflight antes do despacho pago e também protege a chamada direta ao gerador. Nenhum arredondamento, fallback de tamanho, resize, crop ou troca de modelo é aplicado.

`prepare()` sem a opção estrita continua disponível para inspeção dos arquivos históricos e prompts. Isso não prova elegibilidade para geração. Fila, workflow e `generate()` usam `require_supported_canvas=True`. A fila grava bloqueio por SHA da mãe, motivo específico e zero chamadas; a retomada não repete automaticamente a tarefa.

## Evidência e limites

- [Documentação oficial de imagens — seção Earlier GPT Image models](https://developers.openai.com/api/docs/guides/image-generation#earlier-gpt-image-models), consultada em 24/11/2026.
- O [proxy fixado](https://github.com/10/chatgpt-codex-proxy/blob/02f8ce3581c15eb11b2d65daf93c3d4e3bd0e635/internal/server/images.go) encaminha `size` à ferramenta. O contrato da API documentada não comprova que esse transporte respeitará a saída.
- As execuções [45308177395](https://github.com/HelioConde/VideoForge-IA/actions/runs/45308177395) e [45308344517](https://github.com/HelioConde/VideoForge-IA/actions/runs/45308344517) preservaram candidatos C11-P03 rejeitados por canvas. A divergência do pedido não é prova da causa exclusiva dessas saídas.

O relatório passa a guardar `requested_size` junto a `source_canvas` e `provider_canvas`. Os testes usam PNGs sintéticos e provedor simulado; não houve nova geração paga. O QA de saída continua obrigatório, preservando bytes e SHA de candidatos rejeitados e sem repetir chamadas.

## Próxima etapa

Preparar um contrato versionado de fonte/canvas ou placement com coordenadas verificáveis antes de reabrir as tarefas incompatíveis. Não substituir a mãe aprovada, converter candidatos antigos em aprovados, limpar o ledger nem reexecutar tarefas rejeitadas para testar o transporte. Uma futura validação real do proxy precisa de pedido versionado e orçamento/autorização aplicável; o presente ajuste não comprova produção visual corrigida.

Arte, alinhamento, recomposição, rig e publicação continuam sujeitos aos gates existentes.
