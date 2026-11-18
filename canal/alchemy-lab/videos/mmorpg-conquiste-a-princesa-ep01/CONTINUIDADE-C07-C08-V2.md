# EP01 — correção C07/C08: continuidade espacial e narrativa (V2)

**Feedback visual recebido em 18/11/2026:** Elara aparece atrás dos perseguidores apesar de fugir no sentido oposto; os perseguidores parecem ajudar Kael com o carrinho; o carrinho muda de lugar entre cortes; a conversa surge sem um plano de encontro.

Esta versão **não substitui nem apaga** as 39 imagens-mãe do inventário anterior. Substitui **somente a encenação C07+C08** e gera sete novas candidatas V2. A montagem de câmera de 40 tomadas fica preservada como histórico.

**Eixo e geometria obrigatórios:** a fuga de Elara segue da esquerda para a direita da tela; perseguidores atrás vêm da esquerda. O carrinho começa parado contra a parede direita; Kael, sozinho, gira o carrinho sobre as rodas para atravessar e bloquear o beco. Mascarados só ficam do lado esquerdo da barricada, fugitivos do lado direito. Elara escapa para a passagem lateral direita; Kael a alcança na esquina antes de C09. Na cena do carrinho, os perseguidores não tocam o carrinho nem parecem ajudar Kael.

## Linha do tempo corrigida

| ID | Tempo | O que deve acontecer | Fonte |
|---|---|---|---|
| C07-P01 | 69–72 s | Elara corre sozinha | original candidata preservada |
| C07-P02 | 72–75 s | Dois mascarados a perseguem, sem Elara no quadro | nova mãe V2 |
| C07-P03 | 75–78 s | Elara chega a Kael e vê o carrinho parado | nova mãe V2 |
| C07-P04 | 78–82 s | Conversa breve e pedido de ajuda, separado da fuga | antiga C07-P03, candidata reaproveitada |
| C08-P01 | 82–85 s | Kael observa o carrinho antes de tocá-lo | nova mãe V2 |
| C08-P02 | 85–89,33 s | Kael sozinho começa a girar o carrinho | nova mãe V2 |
| C08-P03 | 89,33–93 s | O carrinho forma barreira entre Kael e mascarados | nova mãe V2 |
| C08-P04 | 93–96 s | Elara foge pelo corredor lateral direito | nova mãe V2 |
| C08-P05 | 96–98 s | Kael alcança Elara no lado seguro, preparando C09 | nova mãe V2 |

Total do trecho **870 frames / 29 segundos**. A duração do episódio segue em **4890 frames / 163 segundos**, porém a revisão editorial aumenta de 40 para **42 tomadas**.

## Regras de produção

- Fonte da verdade desta revisão: [CONTINUIDADE-C07-C08-V2.json](CONTINUIDADE-C07-C08-V2.json); demais tomadas permanecem no plano original de 40.
- Todas as novas imagens devem usar referências originais da Bíblia Visual verificadas por SHA; preservar cada PNG antigo.
- Cada Action filha executa no máximo **uma chamada** de geração; não repetir quando existir candidato arquivado; não fazer retry automático de 429.
- Não separar mãos, não criar falsos rigs, não dar aprovação humana automática, não publicar no YouTube.
- Gerar nova mãe não é corrigi-la visualmente até conferência do criador; comparar C07 e C08 por montagem e revisar todos os quadros.
- A revisão V2 do renderer deve **falhar fechada** se faltar qualquer uma das sete imagens novas. Não pode substituir silenciosamente com quadros antigos contraditórios.

## Execução

Validação sem custos: `python -m unittest tests.test_ep01_continuity_v2 tests.test_ep01_camera_batch -v`.

Gerar apenas uma candidata de cada vez: `.github/workflows/ep01-continuity-v2.yml`; a fila do workflow em `push` solicita e verifica uma Action filha por imagem, sequencialmente.

Após as sete imagens estarem arquivadas, renderizar uma nova **prévia técnica** com `python -m videoforge.ep01_camera_batch render --shots all --revision continuity-v2`, em um único MP4 com IDs novos. Até revisão humana, o vídeo deve continuar identificado como prévia sem rig nem áudio.
