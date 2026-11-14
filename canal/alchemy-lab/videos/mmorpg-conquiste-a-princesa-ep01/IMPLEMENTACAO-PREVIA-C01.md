# Prévia técnica do programa — C01-P03

Data: 2026-11-14. Fonte de arte: [seletor atual](rig-selecao-artes-c01.json).
Fonte de movimento: [direção existente](direcao-rig-remotion.json).

Implementação: [programa e execução](../../../../docs/ANIMACAO-POR-DIRECAO.md).
Bindings: [direcao-bindings-c01-draft.json](direcao-bindings-c01-draft.json).

O teste isola os frames absolutos 150–239 (3 segundos, 30 fps). As três
trilhas acionam a mão direita disponível, os ombros e a cabeça baixa de Kael.
Pernas ficam apoiadas; braços, mão e cabeça têm hierarquia. Cabelo e jaqueta
recebem deformação pequena em malhas ancoradas. Aldric, guardas e lanças
permanecem estáticos como contexto visual. Não há tentativa de executar
o saque da espada ou o cruzamento de lanças com peças inadequadas.

Os pivôs vêm das coordenadas provisórias de `split-qa.json`. São dados para
diagnóstico, não medições anatômicas aprovadas. A trilha `kael.punhos` só
possui a mão direita; dedos independentes estão pendentes. Kael está de
costas, portanto não se cria piscada nem olhos novos.

Todas as restrições de arte permanecem: sem geração de imagens, sem IA
de edição, sem aprovação humana inventada. O residual rejeitado não é usado;
Aldric pode conter pixels do trono, e as lanças têm contaminação de fundo.
Faltam underlays, correção de máscaras, revisão dos pivôs e recomposição
aprovada. A prévia tem marca d'água permanente e não contém áudio.

O relatório `coverage.json` cobre 37 planos e 107 trilhas; somente C01-P03
tem bindings de diagnóstico. Isso não altera o status de produção dos
outros planos. C02/C03 continuam rejeitadas. A montagem final de 163 segundos
continua pendente; `renderOfficialAllowed` e `youtubeUploaded` permanecem falsos.

O workflow arquiva MP4 e QA por run. Resultados, SHA do vídeo e URL do run
serão registrados após a primeira execução verificada. Nenhum MP4 de produção
é declarado concluído apenas pela existência deste documento.
