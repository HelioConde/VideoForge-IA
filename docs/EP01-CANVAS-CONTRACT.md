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


## Placement de referência V1 — preparação offline

O módulo `videoforge.ep01_reference_placement` calcula o próximo múltiplo de 16 em cada eixo, preservando orientação, escala 1:1 e posição por translação inteira. Valida o canvas resultante com o mesmo contrato existente; não força elegibilidade de fontes inválidas. O PNG original permanece intocado. O derivado RGBA, com margens transparentes, serve exclusivamente como referência de inspeção.

| Fonte | Canvas candidato | Deslocamento X,Y | Margens esquerda, topo, direita, base |
|---|---|---|---|
| 941×1672 | 944×1680 | 1,4 | 1,4,2,4 |
| 1053×1493 | 1056×1504 | 1,5 | 1,5,2,6 |

O manifesto V1 inclui SHA-256 da fonte e do derivado, retângulo de origem no canvas novo (limites superiores exclusivos), offsets direto/inverso, escala unitária e prova de igualdade dos pixels RGBA na região de origem. O crop do teste é exclusivamente QA. Não gera sprites por recorte, não redimensiona, não substitui a mãe e não modifica registro ou ledger.

Inspecionar uma mãe existente, sem rede/proxy/escrita no repositório:

```sh
python -m videoforge.ep01_reference_placement --shot-id C11-P03
```

A CLI imprime o manifesto e descarta o derivado; a função `prepare_reference` disponibiliza os bytes em memória para QA e integração futura. A geração continua bloqueada pelo preflight estrito. Uma etapa posterior deverá vincular pedido versionado à mãe e ao derivado, conferir dimensões, padding, alpha e placement da saída real, e obter revisão visual antes de usar a transformação na composição. A compatibilidade teórica do tamanho não demonstra suporte efetivo do proxy. Nenhuma chamada paga, aprovação de arte, desbloqueio de rig ou publicação é autorizada por este módulo.

A CI da fila também executa essa CLI sobre a mãe C11-P03 arquivada e publica `ep01-reference-placement-C11-P03.json` no artifact do plano. O manifesto identifica o arquivo original, asset e SHA em `source_proof`; o derivado permanece somente em memória. A prova técnica não autoriza enviar o derivado ao proxy ou usá-lo como peça final.

## QA da candidata no canvas de referência

`inspect_candidate` recompõe o contrato a partir dos bytes originais e de um SHA fornecido separadamente. Rejeita mudanças em dimensões, offsets, escala, SHA do derivado e flags do manifesto. O QA não aceita o próprio original ou o derivado de referência como nova peça.

A candidata deve ser PNG estático RGBA no tamanho exato da referência, incluindo as margens. Não há tolerância automática de um pixel neste contrato novo. As quatro margens precisam ter alfa zero. Dentro do retângulo original, personagens/objetos precisam de transparência e pixels com alfa pelo menos 128; backgrounds precisam preencher esse retângulo com alfa 255. Esse contrato de background aplica-se à futura referência com margens, não altera o pedido opaco do gerador legado.

A caixa de alfa é medida nas coordenadas da fonte. Essa medida não comprova identidade, anatomia, pose, contato, composição ou posição correta. O resultado permanece `placement_verified=false`, `provider_provenance_verified=false`, `human_visual_approval=false` e `rig_ready=false`, mesmo quando canvas e alfa passam. Não produz arquivo de imagem, não corta/redimensiona a candidata, não muda o ledger e não chama o provedor.

Para inspecionar uma peça já arquivada e vinculada à mesma mãe por SHA:

```sh
python -m videoforge.ep01_reference_placement --shot-id C11-P03 \
  --candidate-part character-guarda_direito
```

A CLI verifica o registro e a metadata da candidata. Rejeição técnica é um relatório de diagnóstico (exit 0), não aprovação; erro de proveniência interrompe a inspeção. A CI preserva `ep01-reference-candidate-qa-C11-P03.json` junto do manifesto de referência. A peça histórica 981×1602 continua rejeitada, sem nova cobrança ou modificação.

Próximo passo: construir o pedido versionado com o mesmo contrato de canvas/alpha, fonte e derivado fixados por SHA, e aplicar este QA à resposta original. Nenhum caminho pago ou de animação é desbloqueado automaticamente.

## Pedido versionado e resposta vinculada — modo offline

`videoforge.ep01_reference_request.prepare_request` liga a tomada/componente genérico, SHA da mãe, referência com margens, referências da Bíblia e prompt ao payload de `/v1/images/edits`. Usa ID de componente `<componente>-reference-canvas-v1`, tamanho da referência e fundo transparente inclusive para backgrounds (opacos apenas dentro do retângulo original).

O prompt genérico de canvas é substituído por coordenadas e margens explícitas. Templates inesperados falham. Tomadas bloqueadas por revisão V2/V3, C01-P04 aprovada, componentes já arquivados e revisões especiais com coordenadas próprias não são reabertos por este adaptador. Os bloqueios/recibos do ledger permanecem intactos.

O fingerprint SHA-256 cobre o pedido inteiro, incluindo os bytes anexados, prompt, modelo, papel, fonte e geometria. `inspect_response` exige esse fingerprint fornecido separadamente, relê a mãe e aplica o QA da PR #131 aos bytes originais da resposta. Alterar um campo ou recalcular o hash sem alterar a referência externa não valida o pedido. Fingerprint comprova integridade, não autorização, autoria do provedor ou qualidade artística.

```sh
python -m videoforge.ep01_reference_request --shot-id C11-P03 \
  --part character-kael \
  --source-sha256 9a03b7c13414707b34256c95cfc3d675f80588c9547d54c6374d7bcd26d73603
```

A CLI imprime resumo revisável com prompt, SHA e quantidade de anexos; omite o base64 e marca `summary_only=true`. Esse resumo NÃO pode ser executado/validado como pedido completo. O artifact `ep01-reference-request-C11-P03.json` da CI contém somente esse resumo. O payload completo existe em memória para a futura integração.

Nenhuma função envia HTTP, reserva tarefa, grava PNG ou modifica autorização. `generation_authorized=false`, `provider_calls=0` e os gates de rig/publicação permanecem falsos. Próxima etapa: transporte com reserva durável por ID/fingerprint antes de uma chamada, arquivamento da resposta original e reconciliação sem replay. O QA offline não comprova comportamento real do proxy.


## Reserva persistente antes do transporte

`videoforge.ep01_reference_reservation.reserve_request` prepara a próxima etapa:
reconstrói o pedido a partir das fontes e política atuais, compara o fingerprint
externo e grava uma reserva no **mesmo ledger CAS da fila EP01**,
`runtime/ep01-production-action-queue-v1.json`, na branch
`state/multi-agent-runtime`. A chave `reference_image:<request_id>` independe
do hash: mudar o prompt/hash não permite repetir a mesma versão.

A função só aceita contexto Actions/main deste repositório, com run e tentativa
identificados. O recibo só retorna depois da confirmação da gravação por SHA.
Conflitos entre escritores, timeout e perda de confirmação interrompem a
operação, sem retry. Uma retomada encontra a reserva e exige reconciliação.
Reservas ou chamadas antigas com resultado incerto bloqueiam a nova reserva;
registros antigos concluídos ou barrados no preflight são preservados.

O registro contém somente IDs, hashes, run e flags falsas de aprovação, sem
payload, imagem, prompt ou credenciais. Seu schema é validado também pela fila
antiga. Enquanto houver a reserva, o bloqueio global de tentativas pendentes
da fila impede novos despachos pagos. Não existe liberação automática nem estado
de sucesso artificial. Reservar não afirma que o provedor foi chamado.

**Ainda não ativado em produção:** nenhuma CLI/Action chama a nova função,
nenhuma reserva real foi escrita nesta entrega e não há transporte de imagem.
A CI simula somente a fronteira HTTP do GitHub e exercita o código real de
load/save/CAS, inclusive uma corrida entre dois escritores e confirmação perdida.
Antes de ativar: integrar chamada única, arquivamento dos bytes e reconciliação;
usar o mesmo grupo de concorrência da fila existente e rever a fixture offline
quando a versão for arquivada. O recibo não é autorização de geração e não
pode, sozinho, permitir envio ao proxy.
