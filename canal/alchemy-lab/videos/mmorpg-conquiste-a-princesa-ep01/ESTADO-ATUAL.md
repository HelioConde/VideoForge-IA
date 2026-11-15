# Estado atual — MMORPG: Conquiste a Princesa (EP01)

> **PONTO ÚNICO DE RETOMADA DO EPISÓDIO.** Branch de referência: `main`. Atualizado em 14/11/2026 (horário de Brasília, UTC-3). Antes de alterar qualquer coisa, ler `AGENTS.md`, `docs/MANUAL-PRINCIPAL-ANIMACAO-2D.md`, este documento e `HISTORICO-DESENVOLVIMENTO.md`. **Não começar do zero.**

## Objetivo e limites

Concluir o dorama MMORPG no VideoForge-IA com animação 2D genuína: imagem-mãe → fundo sem personagens → partes originais PNG RGBA → reconstrução de oclusões → pivôs/malhas Three.js → Remotion/ThreeCanvas/SWANGLE → vídeo MP4 → QA visual e audiovisual. Canal: `alchemy-lab`. Vídeo: `mmorpg-conquiste-a-princesa-ep01`.

- Roteiro / direção: 14 cenas de origem, **37 planos cinematográficos**, **107 trilhas de direção** e duração planejada **163 s / 4890 frames em 30 fps**.
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

## Próxima ação concreta, em ordem

1. **Prioridade:** recuperar os **bytes reais dos dois ZIPs já localizados na Library, porém inacessíveis para cópia**, ou enviá-los à raiz `uploads/`; importar os arquivos *já existentes* da C12; verificar exatamente SHA, RGBA, bbox, 941×1672 e presença real no GitHub. Antes de repetir o render, verificar se os ZIPs já apareceram no repositório. Se faltarem, informar `assets_pendentes` e manter o relatório.
2. Quando estiverem arquivados, **o coordenador aciona automaticamente** o workflow técnico C12 na **main**; verificar MP4, repetibilidade de frames, recomposição, bordas, costuras e oclusões. Não inferir aprovação humana do sucesso do workflow.
3. Refinar a C01 com **nuca/gola antes de liberar o rig V2**, depois corrigir máscaras/underlays dos guardas, lanças e Aldric com os pixels aprovados existentes. Não reimplementar as 107 trilhas de direção.
4. Depois ampliar para os demais 36 planos visuais com imagem-mãe própria e rig por cena, narração, legendas e QA; **episódio oficial de 163 s permanece pendente** enquanto não houver assets e aprovação.

## Regra permanente para o próximo agente / próxima conversa

Ao terminar **qualquer avanço no dorama**, atualizar **este arquivo na `main`** com estado e **o próximo passo exato**, e acrescentar um evento em `HISTORICO-DESENVOLVIMENTO.md` com commit, workflow/run, artifact, SHA, QA e pendências. Links de artifact expiram; não tratá-los como arquivamento permanente. Marcar claramente `feito`, `teste_tecnico`, `pendente`, `bloqueado`. Não repetir tarefas concluídas, não mover progresso apenas para branches ou chat, nem sobrescrever histórico anterior. Para regras globais, obedecer `AGENTS.md` e `docs/MANUAL-PRINCIPAL-ANIMACAO-2D.md`.
