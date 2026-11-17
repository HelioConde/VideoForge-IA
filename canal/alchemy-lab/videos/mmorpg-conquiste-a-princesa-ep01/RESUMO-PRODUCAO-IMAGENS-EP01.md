## Snapshot automático e novas imagens — 17/11/2026

**Contagem verificável atual:** [CHECKPOINT-IMAGENS-EP01-AUTO.json](CHECKPOINT-IMAGENS-EP01-AUTO.json) = **12/39 mães originais geradas, 27 faltantes**, 1 abertura preta. A contagem dos trechos históricos antigos (3/36, 5/34 e outros) é obsoleta. O inventário é recalculado automaticamente em cada arquivamento SHA.

**Últimas mães geradas (todas candidatas 941×1672):** C02-P02 [#44084059723](https://github.com/HelioConde/VideoForge-IA/actions/runs/44084059723), C03-P01 [#44084423826](https://github.com/HelioConde/VideoForge-IA/actions/runs/44084423826), C03-P02 [#44085499606](https://github.com/HelioConde/VideoForge-IA/actions/runs/44085499606), C04-P01 [#44085725018](https://github.com/HelioConde/VideoForge-IA/actions/runs/44085725018), C04-P02 [#44085933750](https://github.com/HelioConde/VideoForge-IA/actions/runs/44085933750), C05-P01 [#44086437259](https://github.com/HelioConde/VideoForge-IA/actions/runs/44086437259), C05-P02 [#44087638566](https://github.com/HelioConde/VideoForge-IA/actions/runs/44087638566). Novo mestre da Bíblia para **muralhas de Arken** [#44087301592](https://github.com/HelioConde/VideoForge-IA/actions/runs/44087301592); todos com SHA real no registro.

**Correções de continuidade antes de gastar IA:** referências de C03-P02 alteradas para Kael casual V2, quarto moderno e monitor (anteriormente erradamente medievais); câmera canônica preservada com nota do match cut. Para C05-P02, novo mestre Arken foi gerado primeiro e anexado por SHA junto à estrada.

**QA sem IA:** [C02-C03](QA-C02-C03-CONTINUIDADE-IMAGENS.jpg) e [C03-C04](QA-C03-C04-CONTINUIDADE-QUARTO.jpg). C03-P01 precisa real macro da íris e consistência dos ferimentos; quarto gamer precisa revisão de salto de pose e possível marca casual; nenhum rig está autorizado.

## Correção da auditoria — 17/11/2026

**Contagem válida do registro atual:** 5 tomadas têm imagem-mãe: C01-P02, C01-P03, C01-P04, C01-P05 e C02-P01. São 39 tomadas visuais ao todo, logo **34 sem mãe**. Números históricos de 3/36 presentes mais abaixo representam um momento anterior e foram substituídos por esta conferência.

**C01-P03 V1 reprovada para rig:** QA de recomposição técnica [#44077543911](https://github.com/HelioConde/VideoForge-IA/actions/runs/44077543911) concluiu, mas 58,21% dos pixels ficaram acima do limiar de diferença e a inspeção detectou mudanças de posição/escala de Kael/Aldric e elenco incorreto. Os três PNGs independentes V1 não são reutilizáveis com a mãe V2.

**Mães V2 novas e ainda candidatas:** C01-P03 [#44080234599](https://github.com/HelioConde/VideoForge-IA/actions/runs/44080234599) remove guardas/lanças/espada; C01-P04 [#44080462345](https://github.com/HelioConde/VideoForge-IA/actions/runs/44080462345) corrige postura de Kael, com cópia alinhada em [#44080887693](https://github.com/HelioConde/VideoForge-IA/actions/runs/44080887693). [Comparação V2](QA-MAES-C01-P03-P04-V2.jpg); faltam conferência fina de identidade e pega da lança, **sem aprovação humana**.

**C02-P01**: mãe gerada e arquivada na [execução #44081215706](https://github.com/HelioConde/VideoForge-IA/actions/runs/44081215706), ainda requer QA visual. Nenhum destes avanços libera rig, MP4 ou YouTube.

# EP01 — Estado real das imagens e próximos passos (17/11/2026)

## Checkpoint mais recente — 17/11/2026, após V2 e C02-P01

- **5/39 tomadas visuais possuem imagem-mãe ORIGINAL arquivada**: C01-P02 (rejeitada), C01-P03 (V1 rejeitada e V2 candidata corrigida), C01-P04 (V1 rejeitada e V2 candidata corrigida), C01-P05 (candidata, revisão pendente) e C02-P01 (novo close de Aldric, revisão pendente). **34 tomadas visuais ainda não têm imagem-mãe original.**
- **84 PNGs no registro da Bíblia** no último levantamento: mestres, versões alternativas, máscaras de QA, backgrounds, personagens gerados isolados e cenas-mãe. Não são 84 cenas prontas.
- [C01-P03 V2](assets/geracoes/production-scene-mother-repair-v2/44080234599/c01-p03-scene-mother-v2.png): SHA `bfc1249dc1f83b004b620c333f5aa81689b0ba0c23a3e7573d57c09dcf3539e3`, 941×1672; remove guardas, lanças e espada do primeiro plano, mantém Kael ajoelhado.
- [C01-P04 V2, original](assets/geracoes/production-scene-mother-repair-v2/44080462345/c01-p04-scene-mother-v2.png): SHA `cf19543377960b2100148846f9d77852ca94510c949c62c27b9390e4fbee0f84`, 941×1671, **canvas rejeitado tecnicamente mas PNG arquivado**; [V2 alinhada](assets/geracoes/production-scene-mother-v2-aligned/44080887693/c01-p04-scene-mother-v2-native-aligned-v1.png) SHA `2d11099a536999409a33dae2fc30c517e260c4ad640e41c6942c85b9db499ec5`, 941×1672, apenas uma linha inferior adicional sem IA. Kael agora ajoelhado, rei sentado, guardas com lanças em X. [Revisão assistida](REVISAO-VISUAL-MAES-C01-P03-P04-V2.md) e [prancha V1×V2](QA-MAES-C01-P03-P04-V2.jpg), QA gratuito [#44080972625](https://github.com/HelioConde/VideoForge-IA/actions/runs/44080972625), **sem aprovação humana**.
- [C01-P05 nova cena-mãe](assets/geracoes/production-scene-mother-v2/44079588294/c01-p05-scene-mother.png), SHA `6a599ab681994790b3e9b07bf573817781a448bcf9f77081bc03764448028553`, 941×1672, candidato de mãos/lanças.
- [C02-P01 nova cena-mãe](assets/geracoes/production-scene-mother-v2/44081215706/c02-p01-scene-mother.png), SHA `0d1f8367c76cdf0c9b63f10071406a567b5a5a10cf799e1aa6c5d814019fa2a0`, 941×1672, close de rei Aldric, [geração #44081215706](https://github.com/HelioConde/VideoForge-IA/actions/runs/44081215706) sucesso técnico.
- Os PNGs separados de fundo, Kael e Aldric da C01-P03 foram gerados pelo proxy usando a mãe **V1**, mas a recomposição **reprovou** porque escala/posição se alteraram e mãe incluiu guardas indevidos. **NÃO usar essas peças em V2 ou no rig.** Novas partes devem ser solicitadas ao proxy tomando V2 selecionada/aprovada como referência; não recortar a mãe.
- **Pendente:** revisão visual por responsável, nova geração dos elementos separados de mães V2 aprovadas, revisão de mãos C01-P05, geração das outras 34 imagens-mãe, rig articulado Remotion/Three.js, MP4 e publicação. Todas as aprovações seguem falsas.


## 17/11/2026 — Resultado da recomposição C01-P03: REPROVADO para rig

- **Aldric separado foi realmente gerado pelo proxy** no [run #44076356345](https://github.com/HelioConde/VideoForge-IA/actions/runs/44076356345), PNG 941×1671 SHA `a6eb021cb6c2788530a6fc541831f14d8f99e0392c21de02510f2fdf2312a0f0`. O original foi arquivado e a cópia técnica foi alinhada SEM nova IA para 941×1672 no [run #44076886141](https://github.com/HelioConde/VideoForge-IA/actions/runs/44076886141), SHA `0bcdbc8ef6263bef8c063f1ea696019998efa32a5a45789a9e3054b8b1544285`.
- **QA C01-P03 com três partes separadas do proxy concluído tecnicamente:** [run #44077543911](https://github.com/HelioConde/VideoForge-IA/actions/runs/44077543911). [Comparação verdadeira](QA-C01-P03-PROXY-RECOMPOSICAO.jpg) e [métricas](QA-C01-P03-PROXY-RECOMPOSICAO.json): MAE RGB `36,6056/255`, `58,21%` dos pixels com diferença de intensidade ≥18; Kael RGBA bbox `[0,32,907,1643]`, Aldric `[0,16,941,1671]`.
- **Reprovação da recomposição (inspeção assistida):** escala/posição dos dois PNGs de personagens NÃO reproduzem a mãe. Ambos foram engrandecidos/reposicionados. A mãe C01-P03 também contém guardas com lanças e espada que deveriam ser revelados na C01-P04; foram omitidos indevidamente da separação e estão fora da intenção editorial de C01-P03. Detalhes em [REVISAO-VISUAL-C01-P03-PROXY.md](REVISAO-VISUAL-C01-P03-PROXY.md). A diferença RGB alta também reflete props ausentes, não apenas erro de escala.
- **Correção de regras:** plano C01-P03 passa a declarar **somente Kael e Aldric** visíveis, com guardas/lanças/espada ocultos. Fonte V1 é rejeitada; exige **nova mãe V2 versionada**, sem sobregravar os arquivos existentes. Prompts dos PNGs separados agora exigem escala e bbox exatos, sem zoom/recentragem. Gate impede novas peças da mãe C01-P03 reprovada; testes `tests/test_ep01_proxy_separate_parts.py` e verificação gratuita do plano atualizados.
- **Não usar nenhuma das 3 partes atuais para rig** apesar do padding e da transparência tecnicamente válidos. Não fingir que o gate automático equivale a aprovação humana. `human_approval=false`, `rig_ready=false`, `mp4_generated=false`, `youtube_uploaded=false`.


**Esta é uma fotografia do estado verificado no GitHub; não é autorização de rig, render nem publicação.** Para histórico completo usar `ESTADO-ATUAL.md`, `estado-atual.json` e `HISTORICO-DESENVOLVIMENTO.md`. A [Bíblia Visual](../../biblia-visual/GALERIA-EP01.md) e `../../biblia-visual/REGISTRO-GERACOES.json` têm o registro de cada PNG com SHA e run.

## Contagem real

- **40 tomadas no roteiro**, sendo C01-P01 uma abertura preta sem geração e **39 tomadas visuais**.
- **5 imagens-mãe originais arquivadas** para tomadas distintas: C01-P02 (rejeitada), C01-P03 (V2 em revisão), C01-P04 (V2 em revisão), C01-P05 e C02-P01 (candidatas). **34 imagens-mãe ainda faltam** no fluxo atual. Três arquivos de uma tomada NÃO significam três planos diferentes.
- Na **C01-P03**, a geração separada via proxy já produziu **background** e **Kael** como PNGs independentes; ambos os arquivos originais vieram com 941×1671 em vez de 941×1672. Os arquivos originais foram preservados; geradas novas cópias técnicas com 1 pixel de padding inferior, sem crop, esticar, recompor a mãe ou fazer nova chamada de IA.
- **Aldric separado já gerado, mas recomposição da V1 foi reprovada; novas partes V2, rig e aprovação humana continuam pendentes**. Para C01-P04, só a imagem-mãe está arquivada. C01-P02 permanece bloqueada por anatomia/ornamentos da bainha.
- O registro da Bíblia possui **84 PNGs de diferentes tipos** (referências, reparos, máscaras históricas e cenas). Não são 77 tomadas prontas.

## Fontes e hashes principais

| Papel | Referência | Resolução | SHA-256 | Estado |
|---|---|---|---|---|
| C01-P02 mãe V1 | `production-scene-mother-v2/44036287313/c01-p02-scene-mother.png` | 941×1672 | `b055b93e2174625adb4b7f5eb4f5a40f88f9353bce0fe50e0ac193d6eb002a5e` | Reprovada, não usar no rig |
| C01-P02 patch V4 | `production-contact-repair-v4/44063304090/c01-p02-contact-local-patch-v4.png` | 941×1672 | `3a3d96e9328426c857b1e40d43d0c4edfbe79f07ef9d43c86ef63f6c57f919a9` | Candidata; bocal precisa revisão |
| C01-P03 mãe | `production-scene-mother-v2/44073592014/c01-p03-scene-mother.png` | 941×1672 | `89bc3b1b214fe5286a196171c0dc498041cd29edcf622520ecc25c24b3805765` | Candidata sem revisão visual |
| C01-P03 background via proxy | `production-proxy-separate-part-v1/44074495093/c01-p03-background-clean.png` | 941×1671 | `14d216ed27acda7499404e8c95ac7243c8b3114674453d4321f73f6a12f55991` | Original preservado, canvas rejeitado |
| C01-P03 background alinhado | `production-proxy-separate-alignment-v1/44074895225/c01-p03-background-clean-native-aligned-v1.png` | 941×1672 | `efaf7d320a5635b658f7881453e2b298367536298689927fd0f888aea42c6c07` | Candidata técnica, revisão visual pendente |
| C01-P03 Kael via proxy | `production-proxy-separate-part-v1/44075692204/c01-p03-character-kael.png` | 941×1671 | `20c1f8e07ec164280a478dda8b9db1091aa8b5088290767f0858deff54f58b4e` | Original preservado, canvas rejeitado |
| C01-P03 Kael alinhado | `production-proxy-separate-alignment-v1/44075946150/c01-p03-character-kael-native-aligned-v1.png` | 941×1672 | `a962fad1494c296676879e5a2f1a98c5c68f3349999a75ab39704adec0670889` | Candidata RGBA técnica, revisão pendente |
| C01-P04 mãe | `production-scene-mother-v2/44075357179/c01-p04-scene-mother.png` | 941×1672 | `156a9376298166045654706e75b876a20b7f8201c70d6d494ae9a2b7465f5ab3` | Candidata sem revisão de mãos/lanças |

**Todos esses caminhos são relativos a** `canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/assets/geracoes/`. SHAs não substituem inspeção anatômica ou artística.

## Workflow oficial, agora implementado

1. `ep01-scene-mother-by-request.yml` → gera UMA mãe por tomada com as referências reais SHA-verificadas da Bíblia e o foco de câmera do plano. Contrato corrigido: não preparar sprites via recortes.
2. `ep01-proxy-separate-part-by-request.yml` e `videoforge/ep01_proxy_separate_parts.py` → usa a mãe e os PNGs da Bíblia como **referências** para pedir ao proxy um **novo PNG independente** por background/personagem/objeto. Exige RGBA verdadeiro em personagens/objetos; registra SHA, alinhamento/alpha e nunca aprova arte automaticamente. Uma chamada paga por job; preserva resultado mesmo quando QA reprova tamanho.
3. `ep01-align-proxy-part.yml` e `videoforge/ep01_align_proxy_part.py` → recuperação **offline** de 1–2 linhas inferiores em PNG já gerado; conserva todos os pixels originais, não redimensiona nem extrai conteúdo da cena-mãe e não consome IA. Candidato técnico versionado; ainda depende de recomposição visual.
4. `AGENTS.md`, `docs/CONTRATO-CAMADAS-GERADAS-PELO-PROXY.md` e as oito skills coordenam direção, imagens, rig, QA e montagem. **Não voltar a workflows antigos de source mask ou crop de V1 como imagens finais de rig.**

## Incidentes resolvidos / evidência

- [Pré-voo da C01-P03 #44073458492](https://github.com/HelioConde/VideoForge-IA/actions/runs/44073458492): testes antigos preparavam C01-P02 já arquivada; testes corrigidos sem alterar proteção de produção.
- [C01-P03 mãe #44073592014](https://github.com/HelioConde/VideoForge-IA/actions/runs/44073592014): sucesso com PNG arquivado.
- [Primeiro teste de imagem separada #44073981371](https://github.com/HelioConde/VideoForge-IA/actions/runs/44073981371): colisão de nome com máscaras V1; distinguido por produtor.
- [Segunda tentativa #44074144638](https://github.com/HelioConde/VideoForge-IA/actions/runs/44074144638): Pillow ausente após retorno do proxy, sem salvar PNG. Corrigido instalando e validando dependência **antes** da chamada paga.
- [C01-P03 fundo #44074495093](https://github.com/HelioConde/VideoForge-IA/actions/runs/44074495093): PNG salvo e arquivado, recusado por diferença de 1 linha. [QA de alinhamento #44074895225](https://github.com/HelioConde/VideoForge-IA/actions/runs/44074895225): sucesso sem IA.
- [C01-P04 primeira tentativa #44074952463](https://github.com/HelioConde/VideoForge-IA/actions/runs/44074952463): checagem equivocada do commit HEAD enquanto arquivos eram arquivados; consertada para `GITHUB_SHA` de evento, sem geração nessa tentativa.
- [C01-P04 mãe #44075357179](https://github.com/HelioConde/VideoForge-IA/actions/runs/44075357179): sucesso, imagem candidata arquivada.
- [C01-P03 Kael #44075692204](https://github.com/HelioConde/VideoForge-IA/actions/runs/44075692204): PNG RGBA novo via proxy, recusado por 1 linha; [alinhado #44075946150](https://github.com/HelioConde/VideoForge-IA/actions/runs/44075946150) sem IA. Falhas de QA não são aprovações visuais.

## Próximo passo exato

**Arte:** revisar a anatomia da C01-P04 (mãos fechadas sobre o terço inferior de cada lança, lanças em X alto) e a continuidade do figurino Aldric/Kael; depois pedir ao proxy `C01-P03 character-aldric` em RGBA separado. Não repetir mães/partes SHA arquivadas. Seguir para as outras tomadas com prioridade em imagens-mãe antes do rig.

**QA:** composição lado a lado C01-P03 mãe × background × Kael × Aldric (a gerar), verificar transparência, bordas, postura ajoelhada, detalhes de roupa, regiões ocultas e foco. Sem aprovação visual explícita, não criar rig oficial nem MP4.

**Estado:** `human_approval=false`, `rig_ready=false`, `official_mp4=false`, `youtube_uploaded=false`.
