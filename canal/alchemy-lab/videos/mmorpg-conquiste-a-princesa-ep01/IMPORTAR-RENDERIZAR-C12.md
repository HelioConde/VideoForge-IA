# C12: importar os arquivos existentes e renderizar a prévia de malha

Atualização: 14/11/2026. Fonte: `qa-c12-rig-malha-v2.json`, contrato
`c12-mesh-technical-contract.ts` e Manual Principal de Animação 2D.

O compositor existente usa cinco malhas independentes (512 triângulos), em
C12-P02 e C12-P03. A ponte de importação e Actions está implementada; **o render
real ainda depende dos PNGs ausentes**. Não equivale ao episódio completo nem
ao rig de cabeça, braços e piscadas. C12-P01 continua pendente. O bloqueio de
novas imagens permanece ativo; nenhum comando abaixo chama IA.

## Entradas necessárias

- `alchemy_c12_rig_camadas_tecnicas_v2.zip`: cinco sprites RGBA e dois fundos.
- `confronto_no_trono_real.png` e `princesa_intrigada_no_trono_real.png`, ou
  o ZIP `alchemy-ep01-cinema-3-originais.zip` contendo esses originais.

São nove PNGs reconhecidos pelos hashes já registrados, independentemente do
nome no ZIP. `c12-technical-assets.json` contém os hashes, pivôs e malhas.
As caixas dos recortes foram derivadas dos limites inclusivos dos polígonos
registrados. Sem o ZIP, essa convenção não está confirmada: dimensão divergente
bloqueia a importação para revisão de alinhamento, nunca redimensiona a arte.
Ter o hash em JSON não significa ter o PNG arquivado.

As referências do chat foram aprovadas apenas como preferência estética.
O papel `mother` identifica a origem do recorte técnico, sem aprovar a imagem
como cena-mãe do plano oficial. `sourceOriginalsArchived` prova armazenamento
dos bytes; `sourceProvenance.shotMotherApproved` permanece `false`.

## Importação pelo programa

Na raiz do VideoForge-IA, com os caminhos reais dos arquivos:

```powershell
python -m videoforge.c12_technical_pipeline preflight --source "CAMINHO/alchemy_c12_rig_camadas_tecnicas_v2.zip" --source "CAMINHO/alchemy-ep01-cinema-3-originais.zip"
python -m videoforge.c12_technical_pipeline import --import-id 2026111401 --source "CAMINHO/alchemy_c12_rig_camadas_tecnicas_v2.zip" --source "CAMINHO/alchemy-ep01-cinema-3-originais.zip"
```

`--import-id` é um identificador local positivo e único. O recibo do arquivador
reutiliza o campo histórico `github_run_id`; nesta importação ele **não prova
execução do Actions**. Os bytes são preservados, sem geração ou edição.
Após conferir o recibo e os nove hashes, versionar a pasta indicada por
`archivePath` e enviar a alteração ao GitHub. `prepare` rejeita arquivos que
não correspondam exatamente aos bytes em `HEAD`.

## Actions e revisão

O workflow `c12-technical-render.yml` testa código e publica o preflight nas PRs.
Um teste verde com `foundCount: 0` significa código validado e **assets pendentes**.
Não gera MP4 numa PR. Após a integração do código e dos PNGs em `main`, executar
manualmente “VideoForge - C12 malhas e MP4 tecnico”. O render usa o runner GHCR
existente, ThreeCanvas/SWANGLE, 720×1280, 30fps, 240 frames (8s), sem áudio.

O Actions renderiza duas vezes os quadros 0, 30, 74, 76, 119, 120, 150, 173,
175 e 239, verifica repetibilidade e mudança visível dentro de cada tomada,
registra SHA do MP4, commit/run e mantém a marca de teste sem aprovação humana.
Os PNGs de revisão são arquivados no canal; o MP4 e relatórios ficam no artifact.
Falha no arquivamento é falha do workflow.

Antes de considerar a arte/rig aprovados, revisar recomposição neutra, encaixe
dos recortes, costuras, oclusão, pontas de cabelo e capa em movimento. A checagem
automática de mudança visível não certifica essa qualidade. `fullRigReady`,
`humanVisualReview` e `officialVideoApproved` permanecem `false`; nenhuma
publicação no YouTube é executada.
