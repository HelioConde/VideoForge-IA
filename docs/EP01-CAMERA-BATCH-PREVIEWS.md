> **REVISÃO V2 C07/C08 (18/11/2026):** este documento descreve o lote histórico de 40 tomadas, cujas C07/C08 tiveram problemas de continuidade rejeitados pelo criador. A nova revisão de 42 tomadas preserva 163s; exige 7 novas imagens-mãe candidatas. [Especificação](../canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/CONTINUIDADE-C07-C08-V2.md). Render: `python -m videoforge.ep01_camera_batch render --shots all --revision continuity-v2` **somente após as fontes existirem**. Antes disso o comando falhará deliberadamente.

# EP01 — prévias de câmera retomáveis (17/11/2026)

Implementação técnica autorizada pelo pedido de continuação EP01. Fontes: inventário `CHECKPOINT-IMAGENS-EP01-AUTO.json`, roteiro, plano de 40 tomadas, aprovações individuais e política sem mãos. Nada aqui autoriza publicação, rig ou nova geração.

## Execução

```sh
python -m videoforge.ep01_camera_batch prepare
python -m videoforge.ep01_camera_batch render
python -m videoforge.ep01_camera_batch render --shots C01-P05,C02-P01
```

O workflow manual `ep01-camera-batch-preview.yml` usa o runner Remotion existente, sem instalar dependências ou chamar provedores de imagem. `--shots all` seleciona as 40 tomadas; por padrão apenas C01-P01 a P04. Os outros 36 planos recebem configuração estática conservadora e `direction_reviewed=false`: não são direção cinematográfica concluída. Todas as 39 imagens são verificadas por SHA e dimensões antes do processamento.

Cada configuração contém fonte, aprovação, tempo, enquadramentos, zoom/posição, dolly zero, interesses narrativos, foco, luz, cortes, peças necessárias e QA. A câmera é **zoom digital sobre pintura achatada**; o foco é um filtro global, não profundidade óptica ou parallax. Nenhum código novo movimenta partes do personagem. Não há áudio nesta montagem.

Saída: `output/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/previews/camera-batch-v1/`. Inclui plano de 40 tomadas, props, MP4 e prancha por seleção, montagem e checkpoint. As imagens públicas são cópias por SHA em `motion-remotion/public/vf-ep01-camera-batch/`; não são sprites recortados.

## Retomada e QA

O checkpoint é escrito atomicamente após cada tomada. Uma saída só é reaproveitada se o SHA do MP4 e a impressão digital dos parâmetros, código, lockfile e políticas coincidirem com um relatório que passou pela decodificação integral. Fontes são novamente verificadas antes de consultar o cache. Arquivo existente sozinho não basta.

Em outra máquina/Action, baixar e extrair o artifact anterior no diretório de saída acima antes de executar. Sem restaurar os arquivos, um runner novo renderiza novamente. A Action executa duas vezes o comando para comprovar a retomada dentro do mesmo ambiente.

QA automático: H.264, 540×960, 30 FPS, contagem/duração exatas, decodificação de todos os quadros, detecção de imagens quase pretas fora da abertura e primeiros oito frames da revelação da espada. Pranchas amostram nove momentos. Esses testes não detectam automaticamente anatomia errada, contato impossível, encenação ou qualidade estética; revisão humana continua obrigatória. A tela preta P01 é intencional e não recebe watermark.

## Seleções e limitações conhecidas

- **P02:** SHA original preservado. Contato luva/bainha rejeitado em `REVISAO-ERRO-PAINEIS-C01-P02.json`. O watermark informa diagnóstico; luz revela a pintura, não desembainha a espada. Peças antigas rejeitadas não entram no render.
- **P03:** V3 SHA `e668f713456dd5a41e312885f66c10e2cc033c3aed69ffb7bb577a7d62f79b3d`, ainda não aprovada. Kael olha na direção do rei; rei em pé contrasta com P04 sentado. A câmera não corrige essa continuidade. Revelação suave preserva o eixo, sem espelhar a arte.
- **P04:** original aprovado SHA `a55a2beb23b9015c729ad2099e906fa6062ac76e1ce310b1ab8f4390be2dd1dd`; o novo renderer usa diretamente o PNG original 941×1671, sem confundir com a cópia alinhada usada pelo workflow anterior. Aprovação da fonte não aprova o movimento.
- **Rigs:** inventário histórico C01 usa mãe SHA `544548f0ac5f9e4686e2cf0d1477470f77e2fd7f15678d82799609b678fd6ebf`, diferente das fontes selecionadas, com underlays/pivôs/revisão pendentes. Não habilitar essas partes como se fossem próprias de V3. Peças de cabelo/capa precisam de origem e aprovação próprias antes de malha. Nenhuma mão independente, R3 ou W3 é utilizada.

Há 40 tomadas preparadas, 39 visuais e uma aprovação individual por SHA. Restam 38 tomadas visuais sem aprovação individual. A próxima tomada técnica é calculada em ordem narrativa; a fila de revisão humana é separada. Preservam-se os históricos e a abertura experimental não é o episódio final.

## Regressões encontradas

Os documentos acumulados ultrapassaram os antigos limites de leitura: `estado-atual.json` tinha 107.723 bytes para limite de 100.000; `production-art.json`, 201.085 para 200.000. Os limites foram ajustados para 300.000 bytes, preservando rejeição de symlinks, dados excessivos e validação de schema. Não houve chamada de geração ao testar esses leitores.
