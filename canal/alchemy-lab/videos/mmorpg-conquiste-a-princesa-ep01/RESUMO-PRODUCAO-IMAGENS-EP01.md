# EP01 — Estado real das imagens e próximos passos (17/11/2026)

## 17/11/2026 — Resultado da recomposição C01-P03: REPROVADO para rig

- **Aldric separado foi realmente gerado pelo proxy** no [run #44076356345](https://github.com/HelioConde/VideoForge-IA/actions/runs/44076356345), PNG 941×1671 SHA `a6eb021cb6c2788530a6fc541831f14d8f99e0392c21de02510f2fdf2312a0f0`. O original foi arquivado e a cópia técnica foi alinhada SEM nova IA para 941×1672 no [run #44076886141](https://github.com/HelioConde/VideoForge-IA/actions/runs/44076886141), SHA `0bcdbc8ef6263bef8c063f1ea696019998efa32a5a45789a9e3054b8b1544285`.
- **QA C01-P03 com três partes separadas do proxy concluído tecnicamente:** [run #44077543911](https://github.com/HelioConde/VideoForge-IA/actions/runs/44077543911). [Comparação verdadeira](QA-C01-P03-PROXY-RECOMPOSICAO.jpg) e [métricas](QA-C01-P03-PROXY-RECOMPOSICAO.json): MAE RGB `36,6056/255`, `58,21%` dos pixels com diferença de intensidade ≥18; Kael RGBA bbox `[0,32,907,1643]`, Aldric `[0,16,941,1671]`.
- **Reprovação da recomposição (inspeção assistida):** escala/posição dos dois PNGs de personagens NÃO reproduzem a mãe. Ambos foram engrandecidos/reposicionados. A mãe C01-P03 também contém guardas com lanças e espada que deveriam ser revelados na C01-P04; foram omitidos indevidamente da separação e estão fora da intenção editorial de C01-P03. Detalhes em [REVISAO-VISUAL-C01-P03-PROXY.md](REVISAO-VISUAL-C01-P03-PROXY.md). A diferença RGB alta também reflete props ausentes, não apenas erro de escala.
- **Correção de regras:** plano C01-P03 passa a declarar **somente Kael e Aldric** visíveis, com guardas/lanças/espada ocultos. Fonte V1 é rejeitada; exige **nova mãe V2 versionada**, sem sobregravar os arquivos existentes. Prompts dos PNGs separados agora exigem escala e bbox exatos, sem zoom/recentragem. Gate impede novas peças da mãe C01-P03 reprovada; testes `tests/test_ep01_proxy_separate_parts.py` e verificação gratuita do plano atualizados.
- **Não usar nenhuma das 3 partes atuais para rig** apesar do padding e da transparência tecnicamente válidos. Não fingir que o gate automático equivale a aprovação humana. `human_approval=false`, `rig_ready=false`, `mp4_generated=false`, `youtube_uploaded=false`.


**Esta é uma fotografia do estado verificado no GitHub; não é autorização de rig, render nem publicação.** Para histórico completo usar `ESTADO-ATUAL.md`, `estado-atual.json` e `HISTORICO-DESENVOLVIMENTO.md`. A [Bíblia Visual](../../biblia-visual/GALERIA-EP01.md) e `../../biblia-visual/REGISTRO-GERACOES.json` têm o registro de cada PNG com SHA e run.

## Contagem real

- **40 tomadas no roteiro**, sendo C01-P01 uma abertura preta sem geração e **39 tomadas visuais**.
- **3 imagens-mãe originais arquivadas** para tomadas distintas: C01-P02 (V1 rejeitada visualmente; versões V3/V4 candidatas), C01-P03 e C01-P04 (candidatas). **36 imagens-mãe ainda faltam** no fluxo atual. Três arquivos de uma tomada NÃO significam três planos diferentes.
- Na **C01-P03**, a geração separada via proxy já produziu **background** e **Kael** como PNGs independentes; ambos os arquivos originais vieram com 941×1671 em vez de 941×1672. Os arquivos originais foram preservados; geradas novas cópias técnicas com 1 pixel de padding inferior, sem crop, esticar, recompor a mãe ou fazer nova chamada de IA.
- **Aldric separado, partes de rig, demais objetos, recomposição e aprovação humana continuam pendentes**. Para C01-P04, só a imagem-mãe está arquivada. C01-P02 permanece bloqueada por anatomia/ornamentos da bainha.
- O registro da Bíblia possui **77 PNGs de diferentes tipos** (referências, reparos, máscaras históricas e cenas). Não são 77 tomadas prontas.

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
