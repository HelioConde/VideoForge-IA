# Alchemy Lab — Plano de produção, separação e rigs — Episódio 01

**Status verificado (14/11/2026):** roteiro de 163 segundos e 37 planos registrado. Existem 14 imagens-mãe e camadas candidatas; NÃO existe MP4 oficial nem animação integral aprovada. Esta etapa foi executada sem geração de imagens.

## Regra ativa deste pedido

**NÃO GERAR IMAGENS NOVAS.** Proibido invocar modelos de edição, desenho ou geração de imagem, mesmo em background. As ações permitidas são: salvar arquivos existentes, extrair pixels, gerar máscaras a partir desses pixels, validar SHA/alpha, catalogar, alinhar, organizar as pastas, programar o rig e fazer QA. Manter manual global e não publicar no YouTube.

## Estrutura e proveniência por canal

- assets/referencias/character-bible.png — identidade visual gerada anteriormente.
- assets/cenas-mae/cena-01.png ... cena-14.png — 14 quadros originais do gerador, tecnicamente verificados, não todos aprovados artisticamente.
- assets/proveniencia/ — recibos de geração, hashes SHA-256 e manifestos de origem.
- assets/manifesto-arquivo.json — índice dos 18 PNGs arquivados dos artefatos GitHub Actions (46,8 MB).
- assets/cena-01/candidatos/background-reconstructed.png — salão reconstruído, ainda sem QA final de recomposição.
- assets/cena-01/candidatos/character-group-REJECTED.png — contém pixels indevidos do trono; nunca montar diretamente.
- assets/cena-01/candidatos/kael-rgba-candidate.png — recorte independente, porém contaminado por halo; ainda não é rig.
- assets/cena-01/rig-drafts/kael/ — 12 partições de pixels existentes e split-qa.json; uma camada residual de halo rejeitada.
- assets/cena-01/variacoes-geradas-na-conversa/ — destino dos oito PNGs criados anteriormente no chat, ainda sem upload; são variações não alinhadas à cena-mãe.
- uploads/alchemy-lab-imagens-geradas-anteriormente.zip — entrada temporária opcional para importar oito PNGs do chat, se enviado pelo usuário ao GitHub.

## Cronologia da abertura (fonte: direcao-rig-remotion.json)

| Plano | Frames absolutos | Arte, rig e câmera | Estado |
|---|---:|---|---|
| C01-P01 | 0–59 | Preto absoluto e áudio. | Roteiro |
| C01-P02 | 60–149 | Punho, bainha, lâmina e reflexo independentes; máscara real no desembainhar, sem usar as lanças como espada. | Assets inexistentes |
| C01-P03 | 150–239 | Kael ajoelhado, cabeça baixa, ombros/dedos e respiração sutis; reconstruir áreas ocluídas. | Partições rascunho |
| C01-P04 | 240–359 | Dolly-out real do ThreeCanvas revela dois guardas ATRÁS dele; braços e mãos movimentam as lanças até cruzar em X, com SFX no contato. | Lançase guardas sem rigs validados |

## O que será necessário separar

**Kael:** as 12 partições atuais incluem cabelo, rosto/orelha, tronco/jaqueta, dois braços, antebraço e mão direita, duas pernas e duas botas. Elas são máscaras binárias sobre pixels originais. A recomposição dos pixels visíveis passou, mas não existe anatomia oculta reconstruída, pivô medido ou face com olhos visíveis. Para o olhar furtivo da C12, usar uma arte-mãe em ângulo facial adequado; não desenhar olhos na nuca do Kael.

**Rei Aldric:** cabeça e coroa, olhos e sobrancelhas, boca com visemas sincronizados, barba/cabelo, corpo sem cabeça, braços, mãos e manto. O personagem precisa manter posição sentada diante do trono. A imagem criada anteriormente no chat é uma variação de referência, não recorte fiel 1:1 do quadro da cena-mãe.

**Guarda esquerdo e direito:** dois corpos e rigs separados, ombros, braços superiores, antebraços, luvas/mãos, pernas, capacetes e capas em malha. Cada lança é outro sprite e seu pivô deve ser medido na mão do guarda correspondente, com hierarquia de transformações e sem atravessar outro personagem. As ilustrações das duas lanças do chat não devem substituir automaticamente as armas desenhadas na cena-mãe.

**Trono e cenário:** o salão já foi reconstruído; a variação isolada do trono do chat não está alinhada com a mãe e precisa ser tratada como arte candidata, nunca sobreposta diretamente ao trono existente, pois geraria duplicação.

## QA obrigatório, sem atalhos

1. Preservar a cena-mãe completa, dimensões e SHA. Validar alfa RGBA verdadeiro e áreas escondidas.
2. Excluir de qualquer render os arquivos marcados REJECTED. Cenas-mãe 02 e 03 estão reprovadas visualmente porque revelam Elara antes da hora ou colocam Kael em pé.
3. Partição por máscara é somente uma separação de pixels; o relatório split-qa.json confirma recomposição exata dos pixels visíveis e marca explicitamente underlays, rosto, pivôs e limpeza como pendentes.
4. Criar rig.json somente com sprites individuais adequados, medições de bbox/pivô no canvas original e coordenadas compatíveis. Cabelo/capa requerem malha com raízes fixas.
5. Evitar corpo inteiro flutuando, zoom de PNG achatado, olhos adesivados, rostos transparentes e cabelo/capa duplicados.
6. Só então validar animação frame-driven de Remotion 4 + React Three Fiber/ThreeCanvas com swangle; sem useFrame ou física acumulativa.
7. Registrar QA visual humano separadamente dos testes técnicos. Sem render MP4 completo e aprovado, video_oficial_do_programa=false e youtube_uploaded=false.

## Histórico e links dos arquivos já gerados

- Referência: [43590930215](https://github.com/HelioConde/VideoForge-IA/actions/runs/43590930215)
- Cena C01: [43591342058](https://github.com/HelioConde/VideoForge-IA/actions/runs/43591342058)
- Lote C02–C14: [43591745279](https://github.com/HelioConde/VideoForge-IA/actions/runs/43591745279)
- Fundo e recorte conjunto: [43592098806](https://github.com/HelioConde/VideoForge-IA/actions/runs/43592098806)
- Kael RGBA: [43592844393](https://github.com/HelioConde/VideoForge-IA/actions/runs/43592844393)
- Arquivar existentes no canal: [arquivo de execução](https://github.com/HelioConde/VideoForge-IA/actions/workflows/archive-alchemy-existing-assets.yml)
- Particionar Kael existente sem IA: [arquivo de execução](https://github.com/HelioConde/VideoForge-IA/actions/workflows/split-alchemy-existing-pixels.yml)

## Imagens anteriores geradas nesta conversa

Há um ZIP local de oito PNGs (Aldric; dois guardas e duas versões adicionais; duas lanças; trono). Esses arquivos não estavam nos artefatos anteriores do GitHub. A conexão atual do GitHub não aceita cópia direta desses binários do container. Para importar sem gerá-los outra vez, enviar o ZIP existente à pasta uploads/ pelo GitHub. O workflow import-alchemy-existing-chat-assets.yml valida os SHA-256 e move os PNGs para assets/cena-01/variacoes-geradas-na-conversa/, removendo o ZIP intermediário. Até isso acontecer, NÃO afirmar que as oito imagens estão no repositório.

Referência normativa: docs/MANUAL-PRINCIPAL-ANIMACAO-2D.md e AGENTS.md. A direção quadro a quadro permanece no arquivo direcao-rig-remotion.json.


## 7. Nova etapa: guardas individualizados por pixels, sem IA

A execução [43598226488](https://github.com/HelioConde/VideoForge-IA/actions/runs/43598226488) criou **cinco PNGs candidatos** a partir do antigo `character-group-REJECTED.png`, por máscaras no mesmo canvas e sem IA:

- `guarda-esquerdo-alinhado.png` e `guarda-direito-alinhado.png`: posições derivadas do recorte original; ainda pode haver halo ou bordas incorretas.
- `kael-grupo-alinhado-REJECTED.png`: duplicata do Kael separado; não usar.
- `aldric-com-trono-REJECTED.png`: contém pixels indevidos do trono, não usar como personagem.
- `trono-halo-residual-REJECTED.png`: residual para conferência, nunca no render.

O relatório `assets/cena-01/rig-drafts/grupo/split-qa.json` registra **round-trip exato dos pixels visíveis** e classificação por peça. Isso NÃO significa que os guardas já tenham ombros, braços, mãos, cabeças e capas prontos para rig. A imagem original tem contaminação visual; a decomposição automática apenas organiza o material existente para revisão.

**Totais atuais no GitHub: 18 PNGs originais arquivados + 12 PNGs de partição de Kael + 5 PNGs de partição do grupo = 35 PNGs existentes armazenados neste canal. Nenhum deles foi desenhado de novo nesta etapa.** Oito PNGs exclusivos do chat permanecem em ZIP separado, aguardando upload ao GitHub, com SHA listado em `IMAGENS-EXTERNAS-PENDENTES.json`.


## 8. Extração fiel das duas lanças da cena-mãe, sem IA

A execução [43599262296](https://github.com/HelioConde/VideoForge-IA/actions/runs/43599262296) recortou as duas lanças **diretamente do PNG original** `assets/cenas-mae/cena-01.png`, validado pelo SHA `544548f0ac5f9e4686e2cf0d1477470f77e2fd7f15678d82799609b678fd6ebf`. O procedimento usa máscaras de polígono e linha; não chama nenhum modelo de imagem. Os arquivos estão em `assets/cena-01/rig-drafts/lancas/`:

- `lanca-guarda-esquerdo-CANDIDATE.png`: ponta superior direita, ligada à mão do guarda à esquerda, pivô provisório (381,751), caixa de conteúdo (35,321)–(816,1108).
- `lanca-guarda-direito-CANDIDATE.png`: ponta superior esquerda, ligada à mão do guarda à direita, pivô provisório (644,749), caixa de conteúdo (209,322)–(991,1106).
- `restante-cena-mae-REJECTED-AS-LAYER.png`: residual para confirmar conservação exata, **proibido como sprite móvel**.
- `split-qa.json`: recomposição dos pixels da mãe passou; isso não comprova que as máscaras não incluam fundo, luvas ou reflexos.

**Total salvo no GitHub agora: 38 PNGs**, dos quais três são recortes/residual desta etapa e oito PNGs exclusivos da conversa ainda dependem da importação binária do ZIP. As duas lanças são candidatas, **não** sprites validados para movimentar sozinhas. No plano C01-P04 os braços dos guardas precisam iniciar movimento antes das lanças, respeitando contato e hierarquia; enquanto isso não existir, render oficial bloqueado.

## 9. Inventário verificável e bloqueio editorial

O [inventário da cena 1](rig-inventario-c01.json) e [seu relatório SHA](rig-inventario-c01.qa.json) foram validados pelo [GitHub Actions 43599647856](https://github.com/HelioConde/VideoForge-IA/actions/runs/43599647856): **19 PNGs conferidos**, **16 partes candidatas/rascunho**, **1 peça rejeitada no inventário**, qualidade de rig e publicação **bloqueadas**. O enquadramento 1024×1536 para saída 1080×1920 usa fator 1,25 e corta 100px de cada lateral, sem distorção.

O arquivo [SEM-GERACAO-NOVAS-IMAGENS.lock](SEM-GERACAO-NOVAS-IMAGENS.lock) registra a instrução expressa de NÃO gerar imagens novas. Seis workflows de geração/edição do episódio já consultam esse lock e interrompem antes de chamar IA. Ele se aplica só a este vídeo, não afeta os outros canais. Só poderá ser retirado após novo pedido explícito.
