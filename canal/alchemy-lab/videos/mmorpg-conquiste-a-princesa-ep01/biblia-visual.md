# Bíblia visual v2 — A Missão Impossível / Conquiste a Princesa (EP01)

> **Versão estética escolhida com base nas imagens elogiadas pelo usuário no chat.** Substitui descrições de figurino e cabelo da v1, preservada em [bíblia v1 arquivada](biblia-visual-v1-arquivada.md). Os PNGs originais exibidos no chat ainda não estão importados ao GitHub. Preferência estética NÃO equivale a rig/arte de cena aprovada.
>
> **Regra inalterada:** [SEM-GERACAO-NOVAS-IMAGENS.lock](SEM-GERACAO-NOVAS-IMAGENS.lock). Não gerar arte nem publicar. A animação deve obedecer ao [manual principal](../../../../docs/MANUAL-PRINCIPAL-ANIMACAO-2D.md).

## Referências de estilo e identidade

Os dois quadros aprovados como preferência visual devem orientar rostos, roupas, luz e nível de detalhe. Suas identidades de bytes e SHA-256 estão em [referencias-cinematograficas-aprovadas-no-chat.json](referencias-cinematograficas-aprovadas-no-chat.json); o resultado da validação está em [qa-referencias-chat-cinematograficas.json](qa-referencias-chat-cinematograficas.json).

| Personagem | PNG original no chat (941×1672 RGB) | SHA-256 |
|---|---|---|
| Kael | olhar_tenso_no_salão_real.png | edb751cdb1c1511e56cd8c8f314a788d9adfb9d4338085cead281efa931ed65f |
| Elara | princesa_intrigada_no_trono_real.png | bf199f3e3315fc8357e9fdec7e17db47f2a56c6fca6225b7f4983201fc2fcd6a |

Essas referências são de estética e direção de câmera; não são automaticamente imagens-mãe aprovadas nem camadas RGBA próprias de cada plano.

## Estilo geral do dorama

Manhwa de fantasia romântica 2D, pintura digital refinada e expressiva, vitrais azul-violeta, sombras profundas vinho e cobre, luz dourada lateral atravessando as janelas. Cenário de palácio de pedra, trono dourado e estofado vermelho. Cabelo e armadura com detalhes finos e iluminação coerente entre enquadramentos. Sem CGI 3D, retrato fotográfico, cartoon genérico ou estilos alternados entre cortes. Preferir close facial, plano sobre o ombro, contraplano, detalhes de armas e reações. Não repetir a mesma imagem ampla como se cada tomada fosse uma câmera independente.

## Identidade dos personagens — texto v2

### Kael, 23 anos

- **Rosto:** jovem adulto com traços angulosos, sobrancelhas escuras marcantes, olhos âmbar acastanhados e expressão intensa; no tribunal, poeira, suor e arranhões superficiais coerentes entre tomadas.
- **Cabelo:** castanho quase preto, volumoso e desalinhado, mechas longas irregulares cobrindo parte da testa e caindo perto dos olhos; reflexos cobre nas bordas por luz das janelas. Não voltar ao corte simples da versão 1.
- **Figurino de Arken:** capa/cachecol vinho-vermelho espesso, rasgado e gasto, ombreira de metal escurecido com borda dourada e detalhe de gema azul; roupas escuras por baixo. A versão anterior com jaqueta simples, sem capa ou armadura, não deve contaminar novos planos desta versão.
- **Ação:** Kael não passa a carregar espada por aparecer uma espada sendo desembainhada no insert do tribunal; o objeto pertence a outra pessoa.
- **Olhar C12-P01:** pupilas +12px e pálpebras +1px; cabeça, cabelo, corpo, manto e câmera imóveis. Usar recortes de pupilas e esclerótica restaurada somente após QA visual.

### Princesa Elara, 21 anos

- **Rosto e olhar:** jovem adulta de traço delicado, olhos violeta-lilás, expressão de atenção e surpresa contida, inteligência e decisão política próprias.
- **Cabelo:** loiro dourado longo, ondulado, com trança lateral integrada e pequenas flores brancas e lilases. Não voltar ao cabelo preto da v1.
- **Adornos:** coroa dourada com ametistas roxas, brincos dourados pendentes com cristais violetas e ornamentos florais. No disfarce, não deixar coroa visível sob um capuz simples.
- **Figurino no palácio:** vestido branco-pérola e violeta imperial com bordados dourados e broches roxos; mangas leves; manter a mesma paleta e corte do figurino nos planos e reações.
- **Disfarce:** capa/capuz para mercado e becos que esconda a identidade sem mudar rosto ou cabelo. A revelação de que ela é princesa acontece apenas na cena C12, especialmente C12-P02. Não a revelar no trono durante os planos C01 e C02, mesmo que uma imagem de referência mostre o elenco ao fundo.

### Rei Aldric, 55 anos

Cabelo e barba grisalhos a brancos, barba mais volumosa, coroa dourada, manto vinho e dourado, gola clara; expressão severa e digna. Trono com encosto vermelho profundo e filigranas douradas. Proporção e iluminação consistentes entre plano geral e close.

### Guardas reais e mascarados

Guardas reais em armaduras prateadas ornamentadas, elmos fechados e panos vinho escuro; lanças com a mesma haste, empunhadura e perspectiva entre tomadas. Os mascarados da perseguição vestem roupas escuras e não usam brasão da corte. Na arte-mãe C01 antiga as lanças já estão cruzadas: não fingir que passam de abertas para cruzadas sem anatomia e cenário ocultos reconstruídos.

## Cenários e continuidade

- **Salão do trono:** trono central elevado, escadas vermelhas, colunas de pedra e vitrais azul-violeta; claridade dourada lateral. Guardas nas laterais e rei central. Eixo de 180° respeitado. Princesa não identificável antes da revelação C12.
- **Mercado, becos e quarto contemporâneo:** mesmos elementos de arquitetura, bancas, luz e posição dos objetos entre cortes; a estética 2D de pintura digital não muda na transição para o mundo real.
- **Interface MMORPG:** holograma azul e texto apenas em camadas do Remotion, sem palavras ou menus desenhados na imagem-mãe.
- **Formato:** vídeo 1080×1920, 30 fps; referências aprovadas de 941×1672 são próximas de 9:16, enquanto as 14 mães antigas são de 1024×1536. Não distorcer um retrato para fazê-lo caber em outro canvas.

## Contrato obrigatório da animação

Cada nova tomada: imagem-mãe do ângulo exato → fundo reconstruído sem pessoas duplicadas → peças RGBA da mesma imagem e sem halos → áreas ocultas (underlays) reais → pivôs/ossos/malhas ThreeCanvas → recomposição neutra → QA humano em quadros críticos. Closes são produções de câmera independentes, não um crop da arte geral.

**Estado de migração:** descrição v2 atualizada e v1 histórica preservada. A identidade antiga continua em 14 imagens-mãe e 71 PNGs arquivados; não converter nem reaproveitar automaticamente. A migração de arte só pode avançar com originais de referência por SHA, consistência da nova versão e revisão. Os 36 planos visuais continuam pendentes; MP4 oficial e publicação no YouTube ainda não foram realizados.
