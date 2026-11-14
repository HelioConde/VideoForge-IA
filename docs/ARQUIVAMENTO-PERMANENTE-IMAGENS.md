# Arquivamento permanente das imagens do VideoForge-IA

## Regra

Toda imagem que o VideoForge produz dentro de um GitHub Actions deve ser preservada **na pasta do próprio canal e vídeo**, sem sobrescrita e com SHA-256 e manifesto de proveniência:

`canal/<channel>/videos/<video-id>/assets/geracoes/<producer>/<github-run-id>/`

Os artifacts do Actions são backups com expiração, **não** substituem o histórico no repositório. O programa `videoforge/persist_generated_assets.py` valida cabeçalho PNG, origem e hash; o script `scripts/persistir-imagens-gh.sh` realiza commit/push. O script `scripts/arquivar-pngs-se-existirem.sh` tenta preservar também PNGs produzidos antes de uma falha no QA; sucesso sem PNG é erro.

**Nove workflows de produção** estão conectados a esse procedimento. Nenhum recebe autorização nova de geração nem de publicar no YouTube por causa desse arquivamento.

## Recuperação comprovada de imagens antigas, sem gerar nenhuma

O workflow [recuperar-imagens-antigas-actions.yml](../.github/workflows/recuperar-imagens-antigas-actions.yml) consulta um artifact de um run já realizado, extrai os PNGs existentes, valida a origem e realiza commit no próprio canal. O pedido fica em [recuperar-imagens-do-actions.json](requests/recuperar-imagens-do-actions.json).

Resultados verificados em 14/11/2026:

| Canal / vídeo | Run de origem | PNGs recuperados | Workflow de recuperação |
|---|---|---|---|
| otaku-br / spy-x-family-familia-de-mentira | 43555226353 | 1: `character-bible.png` | [43651551145](https://github.com/HelioConde/VideoForge-IA/actions/runs/43651551145) |
| otaku-br / spy-x-family-familia-de-mentira | 43555469650 | 1: `cena-01.png` | [43651636002](https://github.com/HelioConde/VideoForge-IA/actions/runs/43651636002) |
| otaku-br / spy-x-family-familia-de-mentira | 43560159589 | 3: `background.png`, `cena-base.png`, `character-main.png` | [43651794989](https://github.com/HelioConde/VideoForge-IA/actions/runs/43651794989) |

**Total: cinco arquivos PNG** arquivados em diretórios imutáveis, com bytes e SHA verificados. A `cena-base.png` pode ser byte a byte idêntica à cena-01 de outro run, o que não apaga seu histórico de origem.

A qualidade artística não foi aprovada pela restauração; todos esses manifests mantêm `human_visual_approval=false`. A recuperação não faz inferência, não gera imagens, não cria rigs e não publica vídeos.

[Relatório da referência do Otaku BR](../canal/otaku-br/videos/spy-x-family-familia-de-mentira/assets/geracoes/legacy-action-import/43555226353/manifesto-geracoes.json) · [Relatório da cena](../canal/otaku-br/videos/spy-x-family-familia-de-mentira/assets/geracoes/legacy-action-import/43555469650/manifesto-geracoes.json) · [Relatório das camadas](../canal/otaku-br/videos/spy-x-family-familia-de-mentira/assets/geracoes/legacy-action-import/43560159589/manifesto-geracoes.json)

## Limitação entre imagens do chat e GitHub

Imagens produzidas **dentro do GitHub Actions** são acessíveis ao arquivador e não precisam de ZIP manual. Imagens geradas **na conversa do ChatGPT** residem em outro armazenamento. Um hash ou arquivo exibido no chat não prova que seu binário foi enviado ao repositório. É necessária uma transferência real dos bytes (por exemplo, interface do GitHub em ChatGPT Work ou importação autenticada). Nunca anunciar importação concluída sem ler o PNG remoto e conferir o SHA.

No episódio `alchemy-lab/mmorpg-conquiste-a-princesa-ep01`, os 71 PNGs históricos já arquivados continuam intactos. Os três retratos de referência aprovados no chat (Kael, Elara e C12-P02) ainda **não foram importados ao GitHub**, embora os hashes e o processo de validação estejam preparados. O bloqueio de **não gerar novas imagens** desse episódio continua ativo.

## Testes e verificações

[20 testes aprovados](https://github.com/HelioConde/VideoForge-IA/actions/runs/43651394459): integridade SHA, isolamento por canal e por execução, rejeição de segredo, não sobrescrita, proteção contra saída vazia, arquivos com QA reprovado e integração dos nove workflows.

**Ainda não validado:** um novo job de geração realmente produzindo PNG e automaticamente realizando o commit pela rotina atual. A recuperação de imagens antigas foi testada ponta a ponta e concluiu com sucesso.
