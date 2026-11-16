# EP01 V3 — imagens com a mesma referência de personagens

A imagem C01-P04 foi aprovada pelo usuário como **padrão de APARÊNCIA e estilo** para o julgamento. C01-P05 e C02-P01 foram geradas no próprio GitHub com o PNG original C01-P04 efetivamente ANEXADO à chamada de edição. A referência tem SHA `605ccd361ad9a867eb8b92948010fdbb7d87a031d8b3601c663d815917b1b6cc`.

## Cenas e prévias

| Quadro | Descrição | Imagem e proveniência | Comparação |
|---|---|---|---|
| **C01-P04** | Kael ajoelhado, Aldric, 2 guardas e lanças, plano amplo | [PNG aprovado como referência](assets/geracoes/production-art-request/43965460068/c01-p04-imagem-inicial-v3.png), SHA `605ccd36...` | Âncora |
| **C01-P05** | Mãos e lanças cruzadas dos mesmos dois guardas | [PNG gerado via Actions #43969450680](assets/geracoes/production-art-request/43969450680/c01-p05-guardas-lancas-v1.png), SHA `ad5b4072...` | [Antes/depois lado a lado](QA-C01-P04-VS-C01-P05.jpg) |
| **C02-P01** | Close de Aldric no trono, sem personagens extras | [PNG gerado via Actions #43970462482](assets/geracoes/production-art-request/43970462482/c02-p01-aldric-rosto-v1.png), SHA `a18d2284...` | [Antes/depois lado a lado](QA-C01-P04-VS-C02-P01.jpg) |

Os dois relatórios de comparação ([guardas](QA-C01-P04-VS-C01-P05.json), [Aldric](QA-C01-P04-VS-C02-P01.json)) validam **origem, SHA e anexo real da âncora**. Não validam automaticamente identidade facial, figurinos, número de dedos ou gestos.

## Inspeção visual preliminar dos quadros

- **C01-P05:** os materiais de armadura, lanças, panos vinho, vitrais e iluminação parecem coerentes com o C01-P04. Conferir ergonomia das mãos e pequenos ornamentos antes de aprovar o rig.
- **C02-P01:** Aldric preserva aproximadamente idade, barba grisalha volumosa, coroa dourada, gola de pele, roupa vinho com manto escuro e sala do trono. Há detalhes de coroa e adereços mais desenvolvidos no close: comparar se representam o **mesmo design**, não apenas a mesma paleta.
- **Resolução autêntica:** C01-P04 `941×1672`; C01-P05 `941×1671`; C02-P01 `941×1672`. NÃO deformar os originais.
- **Limite:** Elara ainda não tem âncora aprovada nesta sequência; C01-P04 não pode determinar seu rosto nem seu vestido.

## Produção acelerada

`videoforge.dorama_continuity` exige que novos planos deste elenco recebam o PNG exato e verificado, mantendo elenco compatível. `videoforge.dorama_visual_compare` já cria pranchas JPG com SHA; `.github/workflows/production-art-by-request.yml` agora **tenta gerar e arquivar a comparação automaticamente após cada nova imagem com âncora**, sem IA extra. A ligação automática foi adicionada ao workflow após os dois primeiros renders e **ainda não passou por uma nova geração de ponta a ponta**; a geração de ambas as pranchas acima passou no workflow [#43970937395](https://github.com/HelioConde/VideoForge-IA/actions/runs/43970937395).

**Próximos passos:** conferir os dois quadros, usar a imagem de rosto original de Kael junto com o plano do salão na tomada C02-P02 e seguir a sequência, sem refazer QA de figurinos já aprovados a cada vídeo. Não liberar MP4 final ou YouTube com base apenas na QA técnica.
