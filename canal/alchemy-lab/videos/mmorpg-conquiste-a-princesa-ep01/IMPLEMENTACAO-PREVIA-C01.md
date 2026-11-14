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

## Execução verificada

O [run 43630118130](https://github.com/HelioConde/VideoForge-IA/actions/runs/43630118130)
concluiu com sucesso. Entregou MP4 H264/yuv420p de 90 frames, 1080×1920,
30 fps, sem áudio, com marca d'água. O frame 30 repetido tem hash idêntico;
14.812 pixels da região de arte mudaram no próprio MP4 entre frames 0 e 30
com diferença RGB mínima de 8. A suíte geral passou no Linux: 163 testes,
15 ignorados por condições dos testes existentes.

O [registro de evidência](evidencia-previa-direcao-c01.json) contém hashes,
commit de origem e merge de teste, artefato, formato e métricas. O artefato
do Actions tem retenção de 14 dias. Nenhum binário foi incluído neste commit.

A inspeção do assistente nos frames 0 e 89 confirma a execução, mas mostra
falhas visíveis nos recortes das lanças e nas bordas. A recomposição neutra
não é exata: 1.075.597 pixels diferem da mãe; erro RGB absoluto médio 11,16/255.
Parte dessa diferença vem do fundo reconstruído. Não se converteu esse QA
em aprovação humana ou autorização de vídeo oficial.

## Correção da cintura apontada pelo usuário — 2026-11-14

A primeira prévia abriu uma fenda: `kael.ombros` transladava a jaqueta até
−2 px, enquanto as calças permaneciam imóveis. Além disso, 84 pixels visíveis
da cintura em `[500,1060,20,40]` estavam fora das 11 partições selecionadas.

O binding agora mantém a parte inferior da malha da jaqueta fixa no canvas,
com transição suave entre y=950 e y=985, preservando a respiração dos ombros.
Uma peça de costura recupera somente os 84 pixels ausentes da fonte original
alinhada, sem usar o residual rejeitado inteiro, duplicar pixels ou desenhar
anatomia nova. O teste de regressão verifica a junção nos 90 frames; também
cobre pais com rotação/escala e recusa escalas não invertíveis.

O registro de execução acima corresponde à primeira prévia, anterior a esta
correção. Os novos renders são arquivados pelo workflow do PR #48; os demais
limites de arte, áudio e aprovação continuam explícitos.
