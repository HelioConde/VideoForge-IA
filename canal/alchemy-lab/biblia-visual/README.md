**Correções V2 após revisão visual:** [relatório de desvios](QA-VISUAL-CANDIDATOS.md) · [fila de quatro reparos](FILA-REPAROS-EP01.json). Kael casual V1 ainda veste capa medieval; a lança V1 tem base semelhante a pedestal, base/empunhadura não são closes adequados. O modo `identity_face_only_kael` evita roupa medieval como referência; `master_only` permite close da lança V2 sem importar a haste errada. As 42 referências originais seguem em geração; depois o orquestrador chama `.github/workflows/visual-bible-repairs.yml` em série. Não registrar nada como aprovado sem decisão humana e SHA.

# Bíblia Visual de Alchemy Lab

**Fonte central de personagens, cenários, objetos, interações, variantes antes/depois e histórico de gerações.**

[Índice](INDEX-BIBLIA.json) · [40 tomadas](FILA-EP01.json) · [Plano de mestres EP01](PLANO-MESTRES-EP01.md) · [Regras](REGRAS-PRINCIPAIS.md) · [QA](CHECKLIST-QA-VISUAL.md) · [Referências por SHA](REFERENCIAS-OFICIAIS.json) · [Revisões humanas](REVISOES-MANUAIS.json) · [Gerações](REGISTRO-GERACOES.md)

Cada item possui `ficha.json` e `status.json` gerados a partir do índice. Registro automático por canal mantém caminho, SHA, origem, run, nome, dimensão, estado e histórico sem duplicar PNG. O ato de gerar NÃO aprova arte.

**EP01 continua pausado:** V3 de C01-P04 é referência visual parcial, mas guardas não seguram lanças; V4 também foi rejeitada por direção/pegada na base. As 37 imagens restantes continuam planejadas. Rainha é item futuro, não integrante das 40 tomadas.

## Galeria visual do EP01 (atualização por lote)

Consultar [GALERIA-EP01.md](GALERIA-EP01.md) para visualizar pranchas JPEG leves de **todas as referências-mestre realmente arquivadas**, com link para cada PNG original e SHA. A execução [qa-visual-bible-gallery.yml](../../../.github/workflows/qa-visual-bible-gallery.yml) atualiza a galeria ao concluir cada lote de quatro referências, sem gastar geração de IA, jamais aprovar arte nem alterar o original. O primeiro teste ocorreu em [GitHub Actions #44006804432](https://github.com/HelioConde/VideoForge-IA/actions/runs/44006804432) e foi bem-sucedido.
