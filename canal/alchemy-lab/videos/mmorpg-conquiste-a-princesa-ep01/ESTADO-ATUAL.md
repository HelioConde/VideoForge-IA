# Estado atual — MMORPG: Conquiste a Princesa (EP01)

> **PONTO ÚNICO DE RETOMADA DO EPISÓDIO.** Branch de referência: `main`. Atualizado em 15/11/2026 (horário de Brasília, UTC-3). Antes de alterar qualquer coisa, ler `AGENTS.md`, `docs/MANUAL-PRINCIPAL-ANIMACAO-2D.md`, este documento e `HISTORICO-DESENVOLVIMENTO.md`. **Não começar do zero.**

## DIRETRIZ MAIS RECENTE — QUANTIDADE LIVRE, QUALIDADE ALTA E REGISTRO OBRIGATÓRIO (15/11/2026)

**Regra de produção do responsável:** não estabelecer **nenhum máximo editorial de imagens**. Quando a geração de imagens estiver autorizada, criar e refinar tantas imagens-mãe, vistas de câmera verdadeiramente distintas, cenários, recortes, camadas e expressões quanto o roteiro e o QA pedirem. O único objetivo é dorama **visualmente bonito, detalhado, coerente e animado por ossos/malhas reais**; não simplificar apenas para ficar dentro de cota artificial, nem criar duplicações inúteis. Respeitar custos/limites reais de ferramenta e permissões.

**Este é o arquivo principal e obrigatório do EP01.** Antes de qualquer tarefa, ler o checkpoint atual e confirmar o que há na `main`. Ao terminar qualquer avanço material, incluir neste arquivo: data, cena/plano, trabalho realizado, status, arquivos e SHA, branch/commit, workflows/runs, MP4/artifact se comprovados, QA, erro/bloqueio e **a próxima etapa concreta**. Na mesma integração atualizar `estado-atual.json` e adicionar ao `HISTORICO-DESENVOLVIMENTO.md`; não perder o trabalho nem refazer imagens, cenas, rigs ou renders já existentes. Relatar se ficar em PR/branch e não na main.

**Status desta alteração:** apenas regras/documentação; **0 novas imagens, 0 novos renders e 0 uploads**. O arquivo `SEM-GERACAO-NOVAS-IMAGENS.lock` segue ativo e não é revogado por esta regra; desbloqueio exige autorização explícita. **Estado técnico não mudou:** C01-P03 V5 integrada, QA técnico passou mas falta aprovação visual; C12 depende dos originais ZIP/PNG. **Próxima ação:** verificar visualmente V5 e recuperar os arquivos C12 existentes, antes de executar trabalho adicional.

## Objetivo e limites

Concluir o dorama MMORPG no VideoForge-IA com animação 2D genuína: imagem-mãe → fundo sem personagens → partes originais PNG RGBA → reconstrução de oclusões → pivôs/malhas Three.js → Remotion/ThreeCanvas/SWANGLE → vídeo MP4 → QA visual e audiovisual. Canal: `alchemy-lab`. Vídeo: `mmorpg-conquiste-a-princesa-ep01`.

- Roteiro / direção: 14 cenas de origem, **37 planos cinematográficos**, **106 trilhas de direção atuais após V4 (107 no planejamento original; V3 teve 113)** e duração planejada **163 s / 4890 frames em 30 fps**.
- `SEM-GERACAO-NOVAS-IMAGENS.lock` **continua em vigor**. É permitido importar **imagens originais já existentes**, não produzir novas imagens.
- `video_oficial_do_programa=false`, `human_visual_approved=false` e `youtube_uploaded=false`. Teste técnico de MP4 **não** significa aprovação de personagem, rig ou episódio.
- Manter arquivos de cada vídeo em `canal/<id>/videos/<video-id>/`. O código de componentes reaproveitáveis pode estar em `videoforge/`, `motion-remotion/`, `tests/` e `.github/workflows/`.

## C01 — animação realmente renderizada, rig integrado à main

**Último marco confirmado:** o motor de direção por keyframes, hierarquia de pivôs e malhas foi integrado à `main` no **PR #51**, commit `693212eeb32ede9c0dc8f1c6de94a92638b0dc60`.

- [GitHub Actions run 43660106313](https://github.com/HelioConde/VideoForge-IA/actions/runs/43660106313): **success**, render da prévia técnica **C01-P03** no fluxo já integrado à main. MP4 H.264, **3 s / 90 frames, 1080×1920, 30 fps**, sem áudio, com marca de rascunho.
- Artifact: `directed-rig-alchemy-lab-mmorpg-conquiste-a-princesa-ep01-C01-P03-43660106313`, ID `14139373365`; arquivo temporário de Actions (retém por 14 dias), não mídia arquivada permanentemente no repositório.
- [Run 43660106308](https://github.com/HelioConde/VideoForge-IA/actions/runs/43660106308): **success** no typecheck/regressões.
- Arquivos integrados: `direcao-bindings-c01-draft.json`, `direcao-rig-remotion.json`, `videoforge/directed_rig.py`, `videoforge/directed_rig_qa.py`, `motion-remotion/src/directed-rig-*.tsx` e `.github/workflows/directed-rig-preview.yml`.
- A versão anterior com **costura da cintura de Kael corrigida** foi registrada na [execução 43633018544](https://github.com/HelioConde/VideoForge-IA/actions/runs/43633018544). Reutilizar correções existentes, não reescrever o rig do zero.

**Ainda pendente em C01:** contaminação/cortes nas lanças e nas bordas; underlays/anatomia escondida incompletos; revisão das máscaras de Aldric e dos guardas; prova de recomposição neutra e aprovação humana. Lança já cruzada no quadro de origem não pode ser animada como se estivesse inicialmente aberta. O relatório de C01 indica recomposição provisória com diferença RGB média `11,16/255`; não confundir prova de movimento com prova de qualidade artística.

## C12 — malhas existentes, integração pronta, arquivos originais ainda ausentes

**Não perder o progresso da C12:**

- [Run 43653702785](https://github.com/HelioConde/VideoForge-IA/actions/runs/43653702785): **success** em auditoria de timeline e testes Python; **não renderizou o MP4**.
- [Run 43654314863](https://github.com/HelioConde/VideoForge-IA/actions/runs/43654314863): **success** em contratos/typecheck de Remotion e malha de **5 sprites / 512 triângulos**; **não renderizou o MP4**.
- `qa-c12-rig-malha-v2.json`: registra prova anterior de malha e **MP4 local de 12 s / 360 frames**, `alchemy_c12_mesh_rig_v2_aprovacao.mp4` com SHA `e08f79924e6f09bab195e54d49c32b588c2438d28faf2e1db12d626bba018016`. **Esse MP4 existiu como arquivo local de chat, mas seus bytes não foram arquivados no GitHub; o SHA em JSON não é um download.**
- C12-P01: movimento independente dos olhos de Kael, ainda sem camadas RGBA/underlays de olhos verificadas e prontas no GitHub.
- C12-P02: malha da capa de Kael com **96 triângulos**.
- C12-P03: mecha frontal **100**, cabelo traseiro **144**, brinco **72** e manga **100** triângulos (total **512**).
- O compositor técnico de **8 segundos** `render-alchemy-c12-three-mesh-technical.yml` usa P02+P03; **não substitui** P01 nem a prévia local anterior de 12 segundos.
- [Run 43658221156](https://github.com/HelioConde/VideoForge-IA/actions/runs/43658221156): tentativa de render da C12 na main **bloqueada por ASSETS_PENDING (0/9 originais encontrados)**. [Relatório de bloqueio](qa-c12-render-bloqueio-2026-11-14.json).
- O [PR #50](https://github.com/HelioConde/VideoForge-IA/pull/50) é **outra proposta, ainda aberta**, de importação por hashes/MP4 C12. Analisar e reconciliar com o fluxo já integrado, sem criar duplicidade de renderizadores ou afirmar merge.

**Faltam no GitHub:** duas imagens-mãe RGB dos planos P02/P03, dois backgrounds técnicos e cinco PNGs RGBA isolados (nove arquivos com SHA conhecido). O plano original inclui um terceiro RGB de Kael para P01. Consultar `RENDER-C12-TECNICO.md`, `qa-c12-rig-malha-v2.json` e `IMPORTAR-TRES-REFERENCIAS-ORIGINAIS.md`.

Pacotes **anteriormente produzidos fora do GitHub** e ainda pendentes de importação: `alchemy-ep01-cinema-3-originais.zip` e `alchemy_c12_rig_camadas_tecnicas_v2.zip` (o fluxo de importação da main usa o nome `uploads/alchemy-c12-rig-camadas-tecnicas-v2.zip`). Confirmar bytes reais e SHA antes de marcar importado, jamais regenerar substitutos. Corrigir as máscaras do brinco e da mecha frontal que ainda contêm pele/fundo; verificar underlays e silhuetas.

## 14/11/2026 — avanço registrado: QA do C12, sem alterar a arte

**Novo marco na `main`:** [PR #52](https://github.com/HelioConde/VideoForge-IA/pull/52) integrado no commit `a69287356a87c3bbd2f67bf987ce1a0f0ae73f5c`. [Run de testes 43661690928](https://github.com/HelioConde/VideoForge-IA/actions/runs/43661690928) **SUCCESS** para o contrato; render foi `skipped` no PR. Novos módulos `videoforge/c12_render_qa.py` e `tests/test_alchemy_c12_render_qa.py`:

- Compara **pose neutra** por recomposição de fundo + sprites RGBA com a imagem-mãe 941×1672, usando originais SHA antes de testar movimento. Os limites automáticos não significam aprovação humana.
- Decodifica o **H.264 real** para medir movimento localizado da capa em C12-P02 e de cabelo/brinco/manga em C12-P03, rejeitando MP4 parado ou deslocamento de toda a imagem. Reproduz e compara hashes de dois quadros para testar determinismo; valida 240 frames/30fps.
- [Run de produção técnica 43661756457](https://github.com/HelioConde/VideoForge-IA/actions/runs/43661756457) **FAIL esperado por `ASSETS_PENDING`**, na etapa de preflight dos PNGs. Artifact `vf-alchemy-c12-threecanvas-draft-43661756457` (ID `14140665963`) contém **somente o relatório de pendência, nenhum MP4**. A nova análise neutral/movimento ainda **não foi executada com os originais reais**, e não deve ser declarada aprovada.

**Localização descoberta:** a biblioteca pessoal deste projeto tem metadados dos arquivos **pré-existentes** (não arquivos novos):

- `/youtube/alchemy_c12_rig_camadas_tecnicas_v2.zip` — **6.186.154 bytes**, contém sete PNGs técnicos segundo manifesto anterior;
- `/youtube/alchemy-ep01-cinema-3-originais.zip` — **7.390.768 bytes**, três PNGs RGB de referência;
- `/youtube/alchemy_c12_mesh_rig_v2_aprovacao.mp4` — **999.889 bytes**, prévia local histórica de 12 segundos.

A tentativa de ler/copiar os bytes por integração de arquivos **falhou com `This Project file does not have an authorized raw-byte materialization path`**. **Metadados de Library não provam recuperação dos ZIPs.** Por isso os nove PNGs seguem não arquivados no GitHub. Não copiar conteúdos por aproximação ou gerar artes substitutas.

**Desbloqueio exato:** anexar os **dois ZIPs originais** à conversa como arquivos reais, ou colocá-los diretamente na **raiz** `uploads/` do repositório com os nomes indicados em [RENDER-C12-TECNICO.md](RENDER-C12-TECNICO.md). Depois conferir SHA, importação para `assets/` do episódio, preflight, recomposição neutra, MP4 de 8s, movimentos locais e QA visual (mecha e brinco ainda precisam correção). C12-P01/olhos e episódio completo continuam pendentes.

## 14/11/2026 — importação dos ZIPs agora reativa o MP4 técnico automaticamente

**Implementado na `main`:** [PR #53](https://github.com/HelioConde/VideoForge-IA/pull/53), commit `24c49509b53339a45a413c581435dd817d2028db`. Os workflows de importação dos **três RGB** e **sete PNGs técnicos** já existiam, mas os commits deles feitos com `GITHUB_TOKEN` não disparam outros workflows por `push`. O novo coordenador [`c12-after-import.yml`](../../../../.github/workflows/c12-after-import.yml) escuta a conclusão de **ambos** os importadores (`workflow_run`), consulta a `main` e somente com **nove fontes SHA-256 verificadas** dispara explicitamente `render-alchemy-c12-three-mesh-technical.yml` via `workflow_dispatch` e token Actions autorizado. Origem ausente = **aguardar sem gerar MP4**; origem adulterada/máscara inválida = **erro**.

- [Testes PR run 43662265188](https://github.com/HelioConde/VideoForge-IA/actions/runs/43662265188) **SUCCESS** para o classificador `videoforge/c12_dispatch_gate.py`.
- [Run na main 43662307131](https://github.com/HelioConde/VideoForge-IA/actions/runs/43662307131) **SUCCESS**: confirmou `WAIT_FOR_EXISTING_SOURCE_BYTES` e **não despachou** o render enquanto faltam os PNGs; artifact temporário `c12-after-import-preflight-43662307131` ID `14140133496` só contém relatório.
- Criada a pasta visível [`uploads/README.md`](../../../../uploads/README.md). Enviar pelo GitHub, preservando os PNGs internos, exatamente `uploads/alchemy-ep01-cinema-3-originais.zip` e `uploads/alchemy-c12-rig-camadas-tecnicas-v2.zip`. Os dois ZIPs foram encontrados em metadados da Library, mas **não foi possível acessar seus bytes por esta integração**.
- A prévia C12 de 8 segundos ainda **não existe como novo MP4 de GitHub Actions**; o rig C01 de três segundos permanece disponível na [run 43660106313](https://github.com/HelioConde/VideoForge-IA/actions/runs/43660106313). Nenhuma imagem foi gerada, nenhum vídeo publicado.

## 14/11/2026 — dois ZIPs originais: validação e envio direto para a main

**Nova melhoria integrada:** [PR #54](https://github.com/HelioConde/VideoForge-IA/pull/54), commit `346a3a80c74a96f39390aa12896916bfd2e9a994`. [Workflow de testes 43665498760](https://github.com/HelioConde/VideoForge-IA/actions/runs/43665498760): **SUCCESS** nos testes de contrato, enquanto render da PR permaneceu `skipped`.

- `videoforge/c12_upload_existing_zips.py` valida **10 PNGs existentes** nos dois arquivos ZIP (3 RGB originais e 7 técnicos = 2 fundos + 5 sprites RGBA), exige os SHA e tamanhos nativos cadastrados e recusa arquivos adulterados, descompactação insegura e sobrescritas.
- `scripts/enviar-zips-c12.ps1` oferece um único comando no Windows para fazer clone temporário da `main`, validar ambos os ZIPs, preservar seus bytes e enviar o commit; instruções em [`uploads/README.md`](../../../../uploads/README.md). Não edita arte, não gera imagens e não publica vídeo.
- **Situação real:** pasta `uploads/` da `main` permanece somente com `README.md`. Os ZIPs estão listados na Library, mas a API não liberou acesso aos seus bytes. **Nenhum arquivo RGB/RGBA C12 foi importado e nenhum MP4 novo C12 foi gerado nesta etapa.**
- **Próxima ação exata:** baixar os dois ZIPs antigos da Library para `Downloads` e executar `./scripts/enviar-zips-c12.ps1` em PowerShell dentro do clone do VideoForge-IA; alternativa: anexar os ZIPs à conversa ou enviá-los na pasta `uploads/` do GitHub. Os workflows de importação/coordenação fazem o resto e só renderizam após hashes verificados.

## 14/11/2026 — C01-P03: atuação articulada perceptível V2, ainda não aprovada visualmente

**Feedback do usuário:** a primeira prévia MP4 C01 de 3 s não transmitia movimento. Análise dos keyframes antigos na `main`: cabeça `-0.6°`, ombros `-2 px`, punho `+2°`. Diferença visível insuficiente no plano aberto.

**Correção integrada:** [PR #55](https://github.com/HelioConde/VideoForge-IA/pull/55), commit `c3a4c6bcee3c2cbe5d180bcf1a5355f625a3398a`. Em `C01-P03`, a câmera permanece **travada**, e Kael ganha **seis trilhas de atuação com pivôs independentes**: `kael.punhos/rotationZ`, `kael.ombros/translateY`, `kael.cabeca/rotationZ`, `kael.cabeca/translateY`, `kael.braco-direito/rotationZ`, `kael.antebraco/rotationZ`. Cabelo e jaqueta mantêm suas malhas RGBA existentes, agora com amplitudes 4,2 e 2,8 px. O episódio passou de **107 para 110 trilhas** após adicionar as três ausentes. Coreografia por quadros registrada em [`atuacao-c01-p03-v2.json`](atuacao-c01-p03-v2.json), pedido de render em `pedido-render-c01-direcao.json` revisão 2.

- [PR run 43667345840](https://github.com/HelioConde/VideoForge-IA/actions/runs/43667345840) **SUCCESS** em TypeScript e testes. [PR run 43667345857](https://github.com/HelioConde/VideoForge-IA/actions/runs/43667345857) **SUCCESS** na renderização real de MP4 V2, artifact técnico ID `14143046357` nome `directed-rig-alchemy-lab-mmorpg-conquiste-a-princesa-ep01-C01-P03-43667345857` (retido por prazo limitado).
- MP4 de aprovação técnica V2 (gerado em PR): **3 segundos, 90 frames, 1080×1920, 30fps, H.264, vídeo sem áudio**, SHA256 `1667c60c61b7e10a5e3d5353599631678709e91b456072069ec3e39a1c48094d`.
- QA real decodificado, câmera estática, área de Kael e sem textos: **20.974 pixels** com mudança RGB ≥24 entre frames 0 e 75, contra **11.756** na prévia antiga medida com o mesmo critério/corte (~78% mais); teste mínimo 16.000 passou. Não confundir a métrica com atuação convincente/aprovação artística.
- Após primeira renderização da revisão, foi observada a **faixa cor-de-vinho do cenário exposta na junção da gola**, devido à translação vertical de cabeça sem underlay. Foi reduzida de `-7 px` para `-1,25 px`, mantendo a rotação até `-8,5°`; a faixa **ainda aparece parcialmente** com a rotação. **REVISÃO HUMANA NÃO APROVADA.**
- Permanecem pendentes em C01: reconstrução/overlap da **gola e nuca com pixels originais**, bordas/costuras de mão e ombro, mascaramento do rei/guardas/lanças, QA de recomposição neutra, e movimento convincente para o roteiro completo. Não alegar fechamento de dedos: a mão é um sprite articulado no pulso, sem dedos isolados.
- [Run da main 43667678291](https://github.com/HelioConde/VideoForge-IA/actions/runs/43667678291) **SUCCESS** (teste e render oficial do workflow técnico, NÃO vídeo oficial do programa); artifact ID `14142756569`, nome `directed-rig-alchemy-lab-mmorpg-conquiste-a-princesa-ep01-C01-P03-43667678291`. MP4 da main teve SHA256 `1667c60c61b7e10a5e3d5353599631678709e91b456072069ec3e39a1c48094d`, idêntico byte a byte à prévia do PR; QA decodificado 20.974 pixels; sem nova geração de imagens e sem upload para YouTube. **Visual não aprovado por abertura na gola**.

**Atenção ao manual global:** `docs/MANUAL-PRINCIPAL-ANIMACAO-2D.md` define, para aprovação de rigs, rotação de cabeça absoluta de até 2°. A V2 testa até 8,5° **somente como rascunho técnico experimental não publicável** para avaliar a legibilidade; a exceção não está aprovada e de fato revelou falha de underlay na gola. A animação não pode ser oficializada até cumprir a regra existente, ou até haver revisão fundamentada do rig e das fontes com aprovação expressa do projeto. Não ocultar a divergência nem substituir avaliação visual por contagem de pixels.

**Próxima ação C01:** melhorar a região **nuca/gola** usando apenas as fontes anteriores e QA dos recortes, sem inventar preenchimento/anatomia. Regerar o MP4 da `main`, inspecionar o movimento em close de QA e só então avançar os planos de guarda e rei. Este trabalho não substitui a pendência dos originais de C12.

## 15/11/2026 — C01-P03 V3 integrada e renderizada na `main` (QA técnico passou)

**Situação: `FEITO` no código e no MP4 técnico; `PENDENTE` na aprovação visual.** O [PR #56](https://github.com/HelioConde/VideoForge-IA/pull/56) foi **MERGED** com commit `69e22458703c7c716f05e205987471ce3595b1c5`. É a continuação do rig já existente, sem recomeçar e **sem gerar imagens novas**. O relatório integral de correções, tentativas que falharam e amostras está em [**QA-C01-P03-V3-2026-11-15.md**](QA-C01-P03-V3-2026-11-15.md); roteiro por parte/quadro em [`atuacao-c01-p03-v3.json`](atuacao-c01-p03-v3.json).

- **Sucesso comprovado no PR:** [run de render/QA 43671982404](https://github.com/HelioConde/VideoForge-IA/actions/runs/43671982404) e [run TypeScript/testes 43671982444](https://github.com/HelioConde/VideoForge-IA/actions/runs/43671982444) — ambas `success`.
- **Sucesso reproduzido na main:** [run de render/QA 43673610507](https://github.com/HelioConde/VideoForge-IA/actions/runs/43673610507), **SUCCESS**, e [run de TypeScript/testes 43673610480](https://github.com/HelioConde/VideoForge-IA/actions/runs/43673610480), **SUCCESS**. Artifact técnico da main ID `14145228520`, nome `directed-rig-alchemy-lab-mmorpg-conquiste-a-princesa-ep01-C01-P03-43673610507` (temporário, não arquivo MP4 permanente no GitHub).
- **MP4 real verificado (mesmo SHA entre PR e main):** `directed-rig-preview.mp4`, 3 s, **90 quadros**, **1080×1920**, 30 fps, H.264 `yuv420p`, **sem áudio**, 693.447 bytes. SHA-256 `73993ab7b1f93aead42d1860d16c3db965adcbd3e6bdf2794eb631a9d704100c`.
- **Atuação independente:** `c01-gates-qa.json` confirma **18.923 pixels em movimento** apenas na região de Kael, entre quadros 0 e 75, delta RGB ≥24; gate mínimo 16.000 **PASSOU**. A câmera permanece fixa; a imagem inteira não é deslocada para simular atuação.
- **Junção gola/manga:** no verdadeiro background original verificado por SHA, foram identificados **67, 66 e 73 pixels recém-expostos** nos quadros 55, 75 e 89, dentro da ROI nativa `[495,855,83,28]`. Limite 75, pior = **73**, **PASSOU o gate técnico por margem estreita de 2 pixels**. Não significa que a gola esteja perfeita em inspeção visual.
- **Rig seguro conforme manual:** cabeça no máximo **1,82°** (limite 2°), sem translação Y da cabeça. Nove trilhas neste plano, **113 trilhas de direção no episódio**: cabeça, ombros, braço superior direito, antebraço, pulso, braço esquerdo e flexão independente da **bota direita**; movimentos secundários de cabelo e jaqueta. `kael.costura-gola-pixel-original` é um holdout feito **somente com pixels reais da imagem-mãe** previamente cobertos pela manga e jaqueta, com o mesmo osso `kael.ombros`, atrás das peças. Pixels novos inventados = **0**.
- **QA neutro NÃO aprovado:** `neutral-qa.json` registra `pixelExactRecomposition=false`, média de erro RGB **11,159474** e 1.075.513 pixels diferentes de 1.572.864. Também faltam inspeção visual de recortes na mão, braço, bota/joelho, gola, guardas, lanças e máscara de Aldric/trono. **`humanVisualReview=false`, `publishable=false`, `officialVideoApproved=false`, `youtubeUploaded=false`.**

**Próxima ação C01 (sem refazer o que passou):** revisar visualmente o MP4 V3 no enquadramento final e ampliado, consertar apenas máscaras/underlays existentes sem inventar pixels, melhorar fidelidade neutra à imagem-mãe e separar corretamente rei/guardas/lanças. C01 é **só 3 segundos** dos 163 segundos planejados. Em paralelo, C12 segue `ASSETS_PENDING` (dois ZIPs antigos não importados / nove PNGs originais ausentes). Não retomar o roteiro nem a criação do motor.

## 15/11/2026 — pesquisa GitHub armazenada + direção C01 V4 definida pelo usuário (AINDA NÃO IMPLEMENTADA)

**Estado:** `PESQUISA_ARQUIVADA`, `REGRAS_VISUAIS_C01_ATUALIZADAS`, `V3_REVISADA_PELO_USUARIO_COM_ERROS`, `V4_AINDA_NAO_RENDERIZADA`. A V3 da [run 43673610507](https://github.com/HelioConde/VideoForge-IA/actions/runs/43673610507) permanece **tecnicamente validada** e armazenada como referência, mas **NÃO está aprovada visualmente**. Usuário assistiu e relatou movimentos antinaturais e recortes defeituosos; o sucesso dos dois testes numéricos não revoga esse feedback.

**Documentos permanentes adicionados à `main`:**

- [Pesquisa aprofundada de bibliotecas/skills para rigging 2D](../../../../docs/PESQUISA-SKILLS-BIBLIOTECAS-RIGGING-2D-2026-11-15.md) — comparação de *spine-animation-ai*, *claude-animated-shorts*, Rev2D, Rigby2D, Three.js, OpenCV, scikit-image, IKPy, SAM, PixiJS, Rive, DragonBones, MediaPipe e FFmpeg; casos de uso, licenças a validar, 3 caminhos técnicos, C01/C12, QA e links. Fonte: relatório anexado `Texto colado(1).txt`, SHA-256 `950b66530b071e84e75b82ba5357c31629b8473ae908fc8ec5b1eb49a9256e84`. **Bibliotecas e skills pesquisadas, NÃO instaladas nem integradas.**
- [Regras C01-P03 de respiração sutil e correção de recortes](REGRAS-ATUACAO-C01-P03-RESPIRACAO-2026-11-15.md) — ordem e critérios de aceitação para a **V4**, sem alterar a V3.
- Recomendação técnica: **manter Remotion + Three.js já implantados**, aproveitar métodos de alinhamento OpenCV/segmentação e QA, usar `SKILL.md` como referência organizacional; não trocar de motor nem importar código de licenciamento não comercial sem validação.

**Correções obrigatórias para C01-P03 V4 após feedback visual real:**

1. **Somente Kael respirando**: micro movimento de tórax/ombros (`~±1–2 px` da arte nativa como ponto de partida), cabeça até `~0,5°`, tecido e cabelo com malha minimamente responsiva. Câmera imóvel. Não aumentar o gesto artificialmente para satisfazer `16.000 pixels` de movimento.
2. **Braço/antebraço/punho direitos travados e encostados na perna**; não animar o gesto de punho da V3. Restringir o contato no espaço global, porque apenas travar keyframes locais não impede que ombros móveis arrastem a mão.
3. **Pé e bota direitos inteiramente imóveis**: a track da bota V3 produziu corte/silhueta ruim. Não usar movimento do pé para somar pixels no gate de animação.
4. **Lanças e guardas estáticos, lanças rígidas**; corrigir recortes duplicados e contaminação da máscara.
5. **Rei Aldric com cabeça inteira** na composição neutra original; corrigir máscara/corte antes de aprovar qualquer MP4.
6. **QA apropriado à cena**: comparar frame 0 com arte-mãe, estabilidade dos elementos fixos, mão na perna sem desencaixe, pé sem corte, rei com cabeça íntegra; medir respiração localizada e suavidade, em vez de exigir globalmente a contagem de pixels alta da V3. Tudo sem novas imagens, sem publicação no YouTube.

**Próxima ação C01 exata:** criar uma branch V4 a partir da `main` e **aplicar as regras acima ao rig atual**, executar testes de composição/contatos/máscaras, gerar MP4 de 3 s para revisão humana. **Não executar trabalho de animação por causa do simples arquivamento desta pesquisa.** C12 mantém pendência independente dos ZIPs e PNGs originais.

## 15/11/2026 — C01-P03 V4 integrada, respiração suave e rei/lanças recuperados da mãe

**FEITO no código e no MP4 técnico da `main`. PENDENTE de aprovação visual humana.** [PR #57](https://github.com/HelioConde/VideoForge-IA/pull/57) integrado por squash commit `4d010a92212ce77e9c7fbcf762537ecf0e732be2`. [Relatório completo de implementação, falhas, testes e QA V4](QA-C01-P03-V4-2026-11-15.md); [regras do usuário](REGRAS-ATUACAO-C01-P03-RESPIRACAO-2026-11-15.md); [pesquisa GitHub de skills/bibliotecas](../../../../docs/PESQUISA-SKILLS-BIBLIOTECAS-RIGGING-2D-2026-11-15.md); [JSON da atuação V4](atuacao-c01-p03-v4-respiracao.json).

- **Status verificado:** [PR render 43676494078](https://github.com/HelioConde/VideoForge-IA/actions/runs/43676494078) **SUCCESS**, [PR TS/tests 43676494086](https://github.com/HelioConde/VideoForge-IA/actions/runs/43676494086) **SUCCESS**; [main render 43676630976](https://github.com/HelioConde/VideoForge-IA/actions/runs/43676630976) **SUCCESS**, [main TS/tests 43676630957](https://github.com/HelioConde/VideoForge-IA/actions/runs/43676630957) **SUCCESS**. Artifact técnico da main `14145684036`, nome `directed-rig-alchemy-lab-mmorpg-conquiste-a-princesa-ep01-C01-P03-43676630976`. O binário **só está em artifact temporário do Actions**, não em pasta persistente do GitHub.
- **MP4 real validado:** `directed-rig-preview.mp4`, **3s, 90 quadros, 1080×1920, 30fps, H.264, 599.144 bytes** e **SHA-256 `90baea03b4e2b551a21d341c263853a2e9b9d4d5647314fff46a39bf79fbbff7`**. Verificado **idêntico byte a byte** entre PR e `main`; sem áudio e sem publicação.
- **A animação da C01-P03 é agora apenas respiração:** 2 keyframe tracks (`kael.ombros/translateY` até **-1,25px**, `kael.cabeca/rotationZ` até **-0,32°**). Malha secundária cabelo **0,45px** e jaqueta **0,55px**; câmera parada; episódio passou de **113 para 106 trilhas** de direção, sem alterar os outros 36 planos.
- **Mão/antebraço direito apoiados na perna** e **pé/bota direitos fixos**: a cadeia direita é independente do osso móvel dos ombros, e nenhum keyframe move essas peças; braço esquerdo também não faz gesto. Testes verificam pontos no **espaço global** ao longo dos quadros.
- **Aldric, guardas e lanças recuperados da imagem-mãe original:** a composição utiliza a mãe RGB SHA `544548f0ac5f9e4686e2cf0d1477470f77e2fd7f15678d82799609b678fd6ebf` e copia fundo reconstruído previamente existente apenas sob máscara dos sprites originais do Kael +3px. Recortes estáticos provisórios (`aldric`, guardas e lanças) não são sobrepostos; eles permanecem arquivados para possível trabalho futuro. No frame 0 o **rei com coroa inteira** e as **duas lanças cruzadas originais** foram inspecionados. Não se gerou imagem nova.
- **QA real da `main`:** `c01-gates-qa.json technical_qa_passed=true`. Respiração detectada em **11.115 pixels** da região de Kael (RGB delta≥8, limite V4 25–20.000; regida adicionalmente por pivôs máximos e contatos físicos); rei/coroa, lanças superiores e bota **0 alterações detectadas** entre frames medidos no limiar RGB≥24; gola com **24 pixels** do fundo expostos, abaixo do limite 75. **Não é aprovação visual.**
- **Recomposição muito melhor, mas ainda não exata:** `neutral-qa.json meanAbsoluteRgbError=0,216449949476454`, **13.015 pixels diferentes** em 1.572.864; na V3 eram erro ~11,159474 e 1.075.513 pixels diferentes. `pixelExactRecomposition=false` exige inspeção de contornos Kael, manga, bota/solo, cabelo/gola e máscara alfa. Mantém **`humanVisualReview=false`, `publishable=false`, `officialVideoApproved=false`, `youtubeUploaded=false`.**
- **Histórico de falhas (não apagado):** [run 43676126787](https://github.com/HelioConde/VideoForge-IA/actions/runs/43676126787) falhou devido à proteção da gola tentando seguir braço fixo (referência corrigida). [run 43676244073](https://github.com/HelioConde/VideoForge-IA/actions/runs/43676244073) gerou MP4 mas reprovou um limite de movimento numérico errado para a cena suave; recalibrado sem aumentar amplitudes dos ossos. O relatório V4 detalha essa causa e os resultados verificados.
- **Skills e bibliotecas:** pesquisa de GitHub arquivada e suas práticas de rigging/QA adaptadas ao **Three.js/Remotion existente**; **nenhum código externo não-comercial copiado** e nenhum editor alternativo/IA instalados.

**Próximo passo C01:** assistir ao MP4 V4 em celular e em aproximação para confirmar que a respiração está natural, a mão permanece apoiada, bota sem corte, lanças rígidas e rei inteiro; corrigir qualquer artefato nos poucos pixels de máscara divergentes usando exclusivamente fontes originais. Apenas depois expandir os planos. **C12 continua ASSETS_PENDING**, aguardando ZIPs/PNGs originais; **episódio final de 163s não foi produzido**.

## 15/11/2026 — V5 integrada: costas respiram por malha real, cabeça continua suave

**Estado confirmado no código da `main`:** [PR #58](https://github.com/HelioConde/VideoForge-IA/pull/58) **MERGED**, commit `ae7ca09c3f75ed04498704459a2ac547de810d06`. [Relatório técnico completo V5](QA-C01-P03-V5-2026-11-15.md) com métricas reais, [manifesto do movimento das costas](atuacao-c01-p03-v5-respiracao-costas.json), [manual de rig](../../../../docs/MANUAL-PRINCIPAL-ANIMACAO-2D.md). A V4 permanece como base histórica bem-sucedida.

**Pedido visual:** o usuário gostou do leve movimento de cabeça na V4, mas quer **também as costas se movendo um pouco na respiração**. Portanto, a V5 **mantém** as 2 trilhas `kael.ombros/translateY` até `-1,25px` e `kael.cabeca/rotationZ` até `-0,32°`, **sem gesto extra no braço direito apoiado, bota, guardas, lanças ou rei**. Acrescenta apenas `kael.jaqueta.mesh.backBreath`: deformação independente de vértices do tecido RGB/RGBA já existente na imagem original, com **expansão de até 1,05 px** e **elevação até 0,6 px**, zona Y nativa `857–947` (pico 898); laterais, gola e cintura (sourcePin desde 950) imóveis. A câmera permanece fixa. **A cena continua com 2 tracks e o episódio com 106.**

**Testes e prévia na branch PR:** [render/QA 43680505866](https://github.com/HelioConde/VideoForge-IA/actions/runs/43680505866) **SUCCESS**, [Remotion/TS testes 43680505879](https://github.com/HelioConde/VideoForge-IA/actions/runs/43680505879) **SUCCESS**, após falha inicial [43680421318](https://github.com/HelioConde/VideoForge-IA/actions/runs/43680421318) por tipagem TypeScript TS2345 corrigida. MP4 de 3s/90 quadros/1080×1920 H.264, tamanho **598.863 bytes**, SHA-256 `d84361f693f4e1c83b4d5ad7bd7ed55c253044e672fbf80af803ace58b865481`, artifact PR `14147369278`, temporário. Amostragem real do ROI das costas `[405,870,85,65]` detecta **957/514/8/191 pixels** alterados nos frames 30/55/75/89 (limiar 8), o suficiente para confirmar deformação visível no MP4 técnico. Ator **11.698 pixels** de alteração em ROI ampla; rei/lanças/bota sem mudanças detectadas no limiar 24; gola **24 de 75 pixels** permitidos, QA PASS. Recomposição neutra igual à V4: MAE **0,21645**, 13.015 pixels diferentes em 1.572.864, portanto `pixelExactRecomposition=false`.

**Main após merge confirmada:** [render/QA 43680784142](https://github.com/HelioConde/VideoForge-IA/actions/runs/43680784142) **SUCCESS** e [TS/testes 43680784182](https://github.com/HelioConde/VideoForge-IA/actions/runs/43680784182) **SUCCESS**. Artifact da main `14147374656` (temporário), MP4 H.264 de **3 s / 90 quadros / 1080×1920 / 30 FPS / 598.863 bytes**, SHA-256 `d84361f693f4e1c83b4d5ad7bd7ed55c253044e672fbf80af803ace58b865481`; **bytes idênticos ao MP4 de PR #58**. QA das costas, regiões imóveis e gola passou também na main; ver [relatório definitivo V5](QA-C01-P03-V5-2026-11-15.md). Próxima etapa é **revisão humana da V5 no celular**, especialmente a suavidade das costas e a integridade de cabeça, gola, jaqueta, mão apoiada, bota, rei e lanças. Nenhuma imagem nova; sem YouTube, sem áudio, sem vídeo oficial de 163 segundos. C12 continua esperando os PNG/ZIPs originais. **Não voltar à V4 por falta de memória da conversa; V5 agora é a versão com código mais recente na main, mas não tem aprovação artística.**

## 15/11/2026 — Padrão visual oficial do dorama arquivado (somente editorial)

**Pedido do responsável:** usar o estilo da imagem enviada como amostra para o dorama e fazer com que **quase toda cena tenha clima dramático e ângulo de câmera diferente**, sem perder consistência de Kael, princesa, rei, guardas ou cenários. Nome aprovado neste registro: **Cinematic Semi-Realistic Fantasy Anime** (estilo da ilustração); **Cinematic 2D Mesh Animation** continua o método de animação. A regra é **apenas para o dorama**, não para os outros canais.

- **Bíblia oficial e prompt mestre:** [`PROMPT-OFICIAL-ESTILO-DORAMA.md`](PROMPT-OFICIAL-ESTILO-DORAMA.md). Inclui prompt em inglês parametrizado por plano, negative prompt, 10 tipos de ângulo, tabela de continuidade e checklist de arte.
- **Contratos para agentes:** [`estilo-visual-oficial-dorama.json`](estilo-visual-oficial-dorama.json). O formato marca o escopo do canal, alternância de enquadramentos, qualidade da imagem e autorização **false** para novas imagens do episódio.
- **Amostra arquivada no repositório:** [miniatura autêntica da imagem do usuário, 96×171](REFERENCIA-VISUAL-DORAMA-PREVIEW-96.jpg), sem regeneração por IA, SHA-256 `58f22420d123561623944e369c08c7d6a1808df29dc2e3f5d795129c5d2192b4`. A imagem original enviada tem dimensão **864×1536**, bytes JPEG apesar da extensão `.png`, SHA-256 `2bab99670444001fbccf8a6c861276e93dfb56f04a33ba5f542698ad3419b2e1`; **original em resolução plena NÃO foi versionado no GitHub**. Esta miniatura **não serve para recorte ou rig**.
- **Entrada fixa no canal:** [`canal/alchemy-lab/dorama/README.md`](../../dorama/README.md), [README do canal](../../README.md), [estratégia editorial](../../ESTRATEGIA.md), README e AGENTS globais. Todo agente de imagens **futuras e autorizadas** deverá consultar esse padrão antes de propor novos quadros.
- **Nenhuma alteração de sprites, imagens-mãe, direção do rig V5, assets do C12, workflow, render ou YouTube foi feita** por este registro editorial.
- **Bloqueio ativo preservado:** [`SEM-GERACAO-NOVAS-IMAGENS.lock`](SEM-GERACAO-NOVAS-IMAGENS.lock) continua proibir gerar ou editar imagens novas neste EP01. **Padrão para uso futuro NÃO implica autorização agora**. Para gerar novas imagens deste episódio é necessária autorização explícita de remoção/alteração do bloqueio. O MP4 da C01-P03 V5 permanece [prévia técnica](QA-C01-P03-V5-2026-11-15.md) aguardando aprovação visual humana; C12 continua aguardando originais reais.

**Próxima ação editorial:** quando uma **nova cena/episódio estiver autorizado**, escrever uma ficha por plano com emoção, ângulo realmente diferente, perspectiva, personagens aprovados, luz, geografia e checks de continuidade; somente então aplicar o prompt mestre. **No EP01 atual, continuar com imagens existentes e rig, sem novas gerações.**

## Próxima ação concreta, em ordem

1. **Prioridade:** recuperar os **bytes reais dos dois ZIPs já localizados na Library, porém inacessíveis para cópia**, ou enviá-los à raiz `uploads/`; importar os arquivos *já existentes* da C12; verificar exatamente SHA, RGBA, bbox, 941×1672 e presença real no GitHub. Antes de repetir o render, verificar se os ZIPs já apareceram no repositório. Se faltarem, informar `assets_pendentes` e manter o relatório.
2. Quando estiverem arquivados, **o coordenador aciona automaticamente** o workflow técnico C12 na **main**; verificar MP4, repetibilidade de frames, recomposição, bordas, costuras e oclusões. Não inferir aprovação humana do sucesso do workflow.
3. **C01 V5 já integrada à main e MP4 técnico da main confirmado:** [consultar QA V5](QA-C01-P03-V5-2026-11-15.md), verificar render [da main 43680784142](https://github.com/HelioConde/VideoForge-IA/actions/runs/43680784142), assistir MP4 da V5 no celular, conferir costas respirando suavemente com cabeça ainda leve, mão apoiada, bota sem cortes, rei/coroa e lanças originais. **Não restaurar tracks V3 de braço/pé nem recrear fundos**, preservar V5 com fonte aprovada.
4. Depois ampliar para os demais 36 planos visuais com imagem-mãe própria e rig por cena, narração, legendas e QA; **episódio oficial de 163 s permanece pendente** enquanto não houver assets e aprovação.

## Regra permanente para o próximo agente / próxima conversa

Ao terminar **qualquer avanço no dorama**, atualizar **este arquivo na `main`** com estado e **o próximo passo exato**, e acrescentar um evento em `HISTORICO-DESENVOLVIMENTO.md` com commit, workflow/run, artifact, SHA, QA e pendências. Links de artifact expiram; não tratá-los como arquivamento permanente. Marcar claramente `feito`, `teste_tecnico`, `pendente`, `bloqueado`. Não repetir tarefas concluídas, não mover progresso apenas para branches ou chat, nem sobrescrever histórico anterior. Para regras globais, obedecer `AGENTS.md` e `docs/MANUAL-PRINCIPAL-ANIMACAO-2D.md`.
