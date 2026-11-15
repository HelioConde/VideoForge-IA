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

## Próxima ação concreta, em ordem

1. **Prioridade:** recuperar os **bytes reais dos dois ZIPs já localizados na Library, porém inacessíveis para cópia**, ou enviá-los à raiz `uploads/`; importar os arquivos *já existentes* da C12; verificar exatamente SHA, RGBA, bbox, 941×1672 e presença real no GitHub. Antes de repetir o render, verificar se os ZIPs já apareceram no repositório. Se faltarem, informar `assets_pendentes` e manter o relatório.
2. Quando estiverem arquivados, executar o workflow técnico C12 na **main**, verificar MP4, repetibilidade de frames, recomposição, bordas, costuras e oclusões. Não inferir aprovação humana do sucesso do workflow.
3. Refinar a C01 usando o motor **já integrado**, corrigindo máscaras/underlays dos guardas, lanças e Aldric com os pixels aprovados existentes. Não reimplementar as 107 trilhas de direção.
4. Depois ampliar para os demais 36 planos visuais com imagem-mãe própria e rig por cena, narração, legendas e QA; **episódio oficial de 163 s permanece pendente** enquanto não houver assets e aprovação.

## Regra permanente para o próximo agente / próxima conversa

Ao terminar **qualquer avanço no dorama**, atualizar **este arquivo na `main`** com estado e **o próximo passo exato**, e acrescentar um evento em `HISTORICO-DESENVOLVIMENTO.md` com commit, workflow/run, artifact, SHA, QA e pendências. Links de artifact expiram; não tratá-los como arquivamento permanente. Marcar claramente `feito`, `teste_tecnico`, `pendente`, `bloqueado`. Não repetir tarefas concluídas, não mover progresso apenas para branches ou chat, nem sobrescrever histórico anterior. Para regras globais, obedecer `AGENTS.md` e `docs/MANUAL-PRINCIPAL-ANIMACAO-2D.md`.
