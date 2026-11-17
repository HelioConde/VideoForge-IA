# C01-P03 — Revisão visual assistida, reprovação para rig (17/11/2026)

## Fontes reais
- [Prancha de recomposição](QA-C01-P03-PROXY-RECOMPOSICAO.jpg): A mãe, B composição das três peças via proxy, C mapa de diferenças e D background limpo.
- [Métricas e SHA](QA-C01-P03-PROXY-RECOMPOSICAO.json): `MAE RGB = 36,6056/255`; **58,21%** dos pixels têm diferença de intensidade ≥18 no mapa; quadro 941×1672, 3 entradas independentes SHA verificadas.
- [GitHub Actions #44077543911](https://github.com/HelioConde/VideoForge-IA/actions/runs/44077543911): **sucesso técnico**, não aprovação visual.

## Resultado do exame visual

**Reprovação assistida de recomposição, NÃO aprovação humana.** A diferença não é uma tolerância de 1px; é reencenação em escala diferente.

1. Na mãe, Kael ajoelha-se no **primeiro plano inferior** com capa estendida e Aldric aparece **menor, no meio da cena diante do trono**. Na composição, **ambos foram ampliados e deslocados**: Kael ocupa quase a altura inteira do enquadramento; Aldric passa a ocupar grande parte da metade superior. Os bboxes de alfa gerados são `Kael [0,32,907,1643]` e `Aldric [0,16,941,1671]`. Essas caixas quase cobrem todo o canvas e não condizem com as posições originais.
2. A mãe de C01-P03 **já inclui dois guardas com lanças**, embora a lista de elenco da tomada declare somente `kael` e `aldric`. Essa composição antecipa a revelação prevista em **C01-P04**, e introduz inconsistência entre roteiro, plano e arte.
3. A espada no primeiro plano da mãe não foi criada nesta etapa como peça separada. A ausência na recomposição significa que o contraste RGB global **não deve ser interpretado inteiramente como falha dos personagens**, mas há falha visual inequívoca de escala e recorte de enquadramento nas figuras geradas pelo proxy.
4. O fundo vazio do salão tem aparência coerente como cenário isolado, mas isso não aprova a recomposição completa, a textura do figurino ou a geometria das partes antes ocultas.
5. O alinhamento técnico de 1 linha inferior só corrigiu a altura: **não modificou a escala ou localização dos personagens**. A tentativa não deve entrar em rig.

## Correção de processo

- **Na futura mãe V2 C01-P03**, descrever plano próprio de Kael ajoelhado diante de Aldric com SOMENTE estes dois visíveis, sem guardas e lanças (esses aparecem em C01-P04). Manter uma imagem original versionada, sem sobrescrever a mãe atual.
- Pedir ao proxy um PNG **gerado separadamente** por personagem via edição da **mesma cena-mãe**. Usar instrução inequívoca de manter exatamente a caixa espacial/bbox, a escala aparente e os grandes espaços vazios transparentes do canvas; **nenhum close/zoom, novo retrato nem reencenação**. Não recortar figura com máscara local para virar sprite final.
- Medir os bboxes de cada PNG RGBA e confrontar com o enquadramento real da mãe antes de avançar. Refazer QA de três peças (fundo, Kael, Aldric) mais quaisquer props efetivamente visíveis na mãe escolhida.
- Não aprovar automaticamente baseado em checksum, PNG com alfa, bom alinhamento de 1 px ou sucesso de workflow. QA temporal e ossos ficam bloqueados.

**Situação:** `assistant_visual_review=fail_scale_and_story_cast`, `human_visual_approval=false`, `rig_ready=false`, `mp4_generated=false`, `youtube_uploaded=false`.

Os PNGs originais e os candidatos de alinhamento devem continuar arquivados para comparação. Não gastar novas chamadas repetindo exatamente estes mesmos prompts/fontes.
