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
