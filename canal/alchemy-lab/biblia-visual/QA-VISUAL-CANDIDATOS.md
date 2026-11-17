# QA visual das imagens-mestre — EP01

> Relatório de inspeção preliminar do assistente sobre a primeira prancha JPG SHA-verificada da [Galeria EP01](GALERIA-EP01.md). **Não é aprovação humana.** A análise visual não substitui o PNG original de resolução integral nem registra uma decisão do usuário. Cada imagem continua pendente de revisão em `REVISOES-MANUAIS.json`.

## Defeitos identificados — versões V1 preservadas no histórico

| Prioridade | Arte candidata e evidência | Inspeção visual preliminar | Correção V2 planejada |
|---|---|---|---|
| P0 | [Kael casual / antes V1](../videos/mmorpg-conquiste-a-princesa-ep01/assets/geracoes/production-art-request/44006463096/biblia-kael-casual-antes-v1.png) — SHA `84ff479d3699d05008c31ba659c6f9d6a135034ed3e571201925436aa3f50ae6` | Na prévia, **ainda veste uma grande capa vinho longa e aspecto medieval**, embora a versão seja o protagonista **antes de entrar no MMORPG**. Não tratar o figurino V1 como referência para essa variante. | `biblia-kael-casual-antes-v2`: anexar **somente rosto original SHA-verificado**, roupa moderna: camiseta cinza, jaqueta casual preta, jeans e tênis. Não anexar corpo medieval/V3, não copiar capa/armadura. |
| P0 | [Lança completa V1](../videos/mmorpg-conquiste-a-princesa-ep01/assets/geracoes/production-art-request/44006036546/biblia-lanca-guarda-completa-v1.png) — SHA `710b49e6a39435356cdded9141363e3d064d283d8e61bff95da21a92c955a379` | A extremidade inferior parece **base circular larga de pedestal/estandarte fixo**. Isso não se adequa a uma lança portátil de guarda segurada pelo terço inferior e cruzada no ar. | `biblia-lanca-guarda-completa-v2`: virote/ponteira inferior fina, diâmetro quase igual à haste; **sem suporte, sem plataforma, sem pedestal**. |
| P1 | [Base V1](../videos/mmorpg-conquiste-a-princesa-ep01/assets/geracoes/production-art-request/44006194009/biblia-lanca-guarda-base-v1.png) — SHA `59173823904d297acefcbbe834d5b97be1e93182b5b821987ef07e9e1fc937fd` | A prévia mostra novamente **a lança inteira e um inset**, não um close único da base; repete o formato largo do pé. | `biblia-lanca-guarda-base-v2`: close só do terço inferior, usando exclusivamente o PNG da lança V2 para identidade de objeto. |
| P1 | [Empunhadura V1](../videos/mmorpg-conquiste-a-princesa-ep01/assets/geracoes/production-art-request/44006327786/biblia-lanca-guarda-empunhadura-v1.png) — SHA `a34a131bdd0de07aa28f0e46d3e76c4f9299bb29efb96bfffb3ab3e3ab3c67b9` | A prancha mostra **uma lança quase inteira**, não close do ponto da mão no terço inferior. A peça não permite validar visualmente a área de pegada. | `biblia-lanca-guarda-empunhadura-v2`: close da madeira da área de pega, sem luva desenhada na imagem do objeto. |

## Observações que ainda exigem revisão humana

- As duas representações de **Aldric** e os guardas esquerdo/direito parecem manter um desenho de traje relativamente coeso na primeira prancha. Isso é apenas uma impressão de miniatura, **não aprovação de anatomia, identidade, detalhe ou rig**.
- O **salão do trono vazio** parece de fato sem personagens na primeira prancha. Conferir o PNG original em tamanho completo antes de aprovar geometria/perspectiva, trono e iluminação.
- As demais variantes de **Elara, Kael, cenários, coadjuvantes e objetos** ainda precisam de comparação lado a lado com os mestres e verificação de dedos, acessórios, roupas, estilo e composição.

## Operação e bloqueios

1. As quatro imagens V1 acima ficam **arquivadas** como evidência; não são apagadas, não ganham aprovação humana e não viram automaticamente referência canônica.
2. Os quatro reparos estão registrados em [FILA-REPAROS-EP01.json](FILA-REPAROS-EP01.json) e `production-art.json`. O workflow [visual-bible-repairs.yml](../../../.github/workflows/visual-bible-repairs.yml) só será disparado após as 42 imagens-mestre independentes estarem arquivadas e SHA-verificadas, para evitar chamadas simultâneas ao Codex Proxy.
3. A execução continua com **uma chamada por imagem e sem retry pago**. As variantes V2 são novas candidatas, sujeitas à mesma revisão humana.
4. O modo de interação **`approved_masters_only`** segue bloqueando as mãos e lanças cruzadas até que guardas, lança e poses estejam aprovados. O vínculo das interações com lança já foi atualizado para exigir **a lança portátil V2**.
5. Nenhuma das 40 tomadas foi automaticamente liberada, e nenhum vídeo pode ser publicado por consequência desses candidatos.

**Critério de aceitação da lança no futuro:** cada guarda segura **sua própria haste perto da BASE, no terço inferior**, com polegar e quatro dedos fechados ao redor da madeira, punho contínuo com antebraço/cotovelo/ombro e pontas cruzadas em X acima do centro, sem duplicar braços, soltar lanças no ar nem inverter a direção.

## Segunda inspeção de pranchas — falha de identidade dos coadjuvantes

Revisada a [segunda prancha da galeria](galeria/PREVIA-02.jpg), contendo carrasco, figurantes e três referências de mascarados. Foram observados **erros de identidade**, não simples ajustes estéticos:

| Candidata V1 (PNG original SHA) | Defeito aparente na prancha | Reparação prevista |
|---|---|---|
| [Carrasco V1](../videos/mmorpg-conquiste-a-princesa-ep01/assets/geracoes/production-art-request/44007665783/biblia-carrasco-base-v1.png) — `7c1f8fc4b4d7dba761d30799ee188de8c6b7d3bce5cd4f4e23064b4d5f17b425` | Repete a silhueta, cabelo escuro, capa vinho e traje de Kael, em vez de carrasco distinto. | `biblia-carrasco-base-v2`: adulto robusto de cabeça raspada, couro/carvão, sem capa, fonte apenas ambiente vazio. |
| [Figurantes V1](../videos/mmorpg-conquiste-a-princesa-ep01/assets/geracoes/production-art-request/44007811797/biblia-figurantes-base-v1.png) — `dcbdb4383a5d8cb1c0c0b778de36773058f5da345239caa3f54d4493b5aec615` | Gera **um homem com capa vinho**, não uma prancha de pessoas comuns distintas do mercado. | `biblia-figurantes-base-v2`: quatro civis separados (idoso comerciante, vendedora, aprendiz e artesã), sem herói. |
| [Mascarado 1 V1](../videos/mmorpg-conquiste-a-princesa-ep01/assets/geracoes/production-art-request/44007936020/biblia-mascarado-1-base-v1.png) — `7102378830dec69d24fcca8d706c915e87648a06ccba3f310536a660a1eb7abb` | O rosto está **descoberto e se assemelha a Kael**, com capa de herói, em vez de máscara integral. | `biblia-mascarado-1-base-v2`: homem alto/esguio, máscara de prata geométrica fechada, roupa escura verde-acinzentada. |
| [Mascarado 2 V1](../videos/mmorpg-conquiste-a-princesa-ep01/assets/geracoes/production-art-request/44008127022/biblia-mascarado-2-base-v1.png) — `159ddbda6ed18001eefee575f4e394f13724c206b3ce4489d5116e2e45944cdf` | Também parece herói sem máscara, com o mesmo figurino vinho. | `biblia-mascarado-2-base-v2`: corpo baixo/robusto, máscara preta marcada, casaco marrom/oliva, muito diferente do 1. |
| [Mascarados em grupo V1](../videos/mmorpg-conquiste-a-princesa-ep01/assets/geracoes/production-art-request/44008263650/biblia-mascarados-base-v1.png) — `54426224625f945a0c5620aba04752cc31ac5ea1f9aa3ab483033d4cc658dfc0` | Gera **um guarda de armadura e pluma** em vez dos dois perseguidores mascarados. | `biblia-mascarados-base-v2`: incluir exclusivamente os PNGs SHA dos dois mascarados V2; duas figuras inteiras separáveis. |

**Causa técnica provável:** o modo `style_scene` anexava o quadro C01-P04 V3 contendo Kael e guardas à geração de personagens novos; o modelo copiou identidades e figurinos em vez de usar a arte somente como referência estilística. Para corrigir, o modo `style_environment_only` anexa o **salão do trono vazio** com SHA `1397aebed67213d0593ac32d1d7ba8d6a83511d39212368639833bec52cb43ee`, sem pessoas, e seus prompts proíbem copiar protagonistas/guardas. `master_only` agora serve também aos cenários/objetos que exigem continuidade e à dupla de mascarados. Essas modificações foram aplicadas antes de gerar os ambientes e props remanescentes.

**Novas prioridades:** [FILA-REPAROS-EP01.json](FILA-REPAROS-EP01.json) contém agora **9 reparos V2**; os quatro anteriores mais esses cinco. As interações `perseguicao-beco` e `espada-desembainhada` dependem dos personagens V2, sujeitos à aprovação humana. Nenhum dos PNGs V1 acima será automaticamente promovido ou apagado.

## Falha técnica da fila e recuperação segura

- O lote [#44008654469](https://github.com/HelioConde/VideoForge-IA/actions/runs/44008654469) terminou em falha porque o plano `production-art.json` ultrapassou o limite de **200.000 bytes** ao cadastrar as cinco correções. O pedido de estrada [#44009046765](https://github.com/HelioConde/VideoForge-IA/actions/runs/44009046765) falhou na etapa `read_plan` com `PRODUCTION_ART_PLAN_MISSING`, **antes de chamar o provedor de imagem**; não gerou PNG.
- O plano foi compactado sem retirar referências SHA ou os gates e passou a medir **196.708 bytes UTF-8**; os dois workflows de QA que tinham falhado voltaram a ficar verdes em execuções posteriores.
- A [fila principal](FILA-GERACAO-MESTRES.json) foi reativada via push [#44009318478](https://github.com/HelioConde/VideoForge-IA/actions/runs/44009318478), com código que procura o **primeiro PNG faltante por SHA**, evitando refazer as 26 referências já arquivadas no ponto de falha.
- No encerramento dos 42 mestres, o orquestrador aciona `visual-bible-repairs.yml` para os 9 reparos, em série, **uma chamada por run e sem retry cobrável**. As 12 interações e 40 tomadas continuam bloqueadas por revisão humana.

A percepção visual da prancha constitui **relatório preliminar do assistente**, não decisão humana. As aprovações/rejeições manuais continuam exclusivas de `REVISOES-MANUAIS.json`.

## 17/11/2026 — 42/42 mestres gerados; duas V2 recuperadas

- Concluídas e registradas **42 das 42 referências independentes** da fila inicial. Isso mede somente arquivos reais com SHA, **não aprovação visual**.
- A [galeria atualizada, prancha 4](galeria/PREVIA-04.jpg) exibe os dois primeiros reparos V2 reais. **Observação preliminar por inspeção de miniatura:** [Kael antes V2](../videos/mmorpg-conquiste-a-princesa-ep01/assets/geracoes/production-art-request/44011899028/biblia-kael-casual-antes-v2.png) (SHA `a9bfad6ba00f7ea1e3f9af33e3943d572e3e3918d41a29eceefd98df169a4dcd`) agora tem roupa casual moderna — jaqueta preta, camiseta escura, jeans e tênis, **sem capa medieval**. Comparar semelhança facial na resolução original antes de aprovar.
- A [lança completa V2](../videos/mmorpg-conquiste-a-princesa-ep01/assets/geracoes/production-art-request/44012069505/biblia-lanca-guarda-completa-v2.png) (SHA `b6fb64fe457b6b87415176110d5169fa2afef4e61d859bc56ece858d8727d072`) aparece como **haste portátil reta com ponteira inferior estreita**, sem pedestal circular. Isso corrige visualmente o principal erro V1 na miniatura, mas a pegada real de mãos/rig **não foi gerada nem aprovada**.
- O [workflow de reparos #44011835649](https://github.com/HelioConde/VideoForge-IA/actions/runs/44011835649) falhou na terceira candidata, `biblia-lanca-guarda-base-v2`, na [execução #44012198030](https://github.com/HelioConde/VideoForge-IA/actions/runs/44012198030), **antes de chamar a IA**: o teste `test_spear_base_v2_uses_only_corrected_complete_spear` ainda esperava uma lança V2 inexistente quando ela já estava arquivada. Foi corrigido para verificar a fonte SHA real e impedir corpo/pedestal antigo. A CI [#44015257638](https://github.com/HelioConde/VideoForge-IA/actions/runs/44015257638) passou.
- Uma tentativa de rerun do job gerou uma nova execução filha `#44015381933`, mas o monitor antigo confundiu o título repetido com o **run fracassado anterior**. A correção de fluxo no commit `c3d833f9c479529a014dfc188ca960efd11de429` agora identifica a tentativa (`GITHUB_RUN_ATTEMPT`) e captura o **ID exato** retornado pelo despacho, impedindo assistir à execução errada.
- A ordem segura continua sendo: verificar se `#44015381933` gerou e arquivou a base V2, prosseguir **apenas** com variantes ainda ausentes, deixar a galeria refletir o progresso, e não liberar as 12 interações/40 tomadas até evidência de revisão humana.
