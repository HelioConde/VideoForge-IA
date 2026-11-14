# Alchemy Lab

Identificador: `alchemy-lab` · idioma: `pt-BR`.

> **Leia primeiro a [estratégia editorial deste canal](ESTRATEGIA.md).** Ela complementa as regras compartilhadas do projeto e é obrigatória para futuras propostas de pauta, roteiro, artes e análise.
>
> **Direção editorial:** laboratório de doramas em pt-BR, com mini-histórias originais, romances, dilemas e reviravoltas ilustrados por IA. Pesquisar tendências verificáveis, testar formatos e registrar aprendizados sem afirmar performance inexistente. O `gerador_padrao` atual é apenas provisório e não significa que o gerador de dorama já exista.

- `canal.json`: identidade, parâmetros e modelo padrão; YouTube desconectado e uploads desabilitados.
- `editorial/candidatos.json`: pautas pesquisadas (atualmente vazio).
- `editorial/reservas.json`: reservas antirrepetição (atualmente vazio).
- `editorial/pesquisas/`: futuras fontes públicas datadas, sem inventar métricas.
- `conteudos/indice.json`: índice de referências, não fila de geração.
- `videos/<video-id>/video.json`: configuração de cada vídeo (ainda não existe um vídeo aprovado).
- `output/alchemy-lab/videos/<video-id>/` (na raiz do projeto): MP4, mídias e QA fora do Git.

**Estado:** Canal catalogado; sem integração de geração nem YouTube. Nenhuma produção nem aprovação editorial está implícita nestes arquivos.


## Continuidade do elenco em 37 tomadas (EP01)

O novo contrato [continuidade-figurinos-37-planos.json](videos/mmorpg-conquiste-a-princesa-ep01/continuidade-figurinos-37-planos.json) registra o mesmo rosto/cabelo dos protagonistas e a variação deliberada de roupas entre realidades: Kael no tribunal com capa vinho, Kael no mundo moderno (C04) e Kael em Arken; Elara incógnita no mercado/becos (C07–C10) e princesa em branco-violeta somente da revelação C12 em diante.

O motor `videoforge/cinematic_identity_continuity.py` impede que um QA marque como aprovada uma tomada com hash de referência diferente, roupas trocadas ou revelação precoce. Mesmo nos inserts sem personagens principais das cenas C01–C02, exige revisão humana de que a princesa **não aparece identificável ao fundo**. Essas verificações são reaplicadas antes de entregar o rig ao Remotion. Aprovação de estética não equivale a arte final.

- [Execução dos testes de continuidade](https://github.com/HelioConde/VideoForge-IA/actions/runs/43647560925) — 14 testes aprovados, sem gerar imagem ou MP4.
- Os originais dos dois retratos de referência ainda **não foram importados no repositório**. O lock `SEM-GERACAO-NOVAS-IMAGENS.lock` permanece ativo; nenhum dos 36 planos visuais foi declarado pronto.

## Pacote único de três referências cinematográficas

O pacote ZIP original de Kael, Elara e do plano sobre o ombro `C12-P02` pode ser importado em uma única operação, **sem gerar ou alterar os três PNGs**. O script `scripts/enviar-referencias-cinema.ps1` confere os SHA-256 no Windows e envia o ZIP para `uploads/`; o workflow de referência extrai e confere novamente cada arquivo. [Instruções completas](videos/mmorpg-conquiste-a-princesa-ep01/IMPORTAR-TRES-REFERENCIAS-ORIGINAIS.md).

A foto do trono é candidata à câmera C12-P02, **não um rig aprovado**. O workflow não libera imagens-mãe específicas, meshes, MP4 ou YouTube, e os 71 PNGs antigos continuam preservados.

## Estilo aprovado no chat — Kael e Elara (v2)

A nova **[bíblia visual descritiva v2](videos/mmorpg-conquiste-a-princesa-ep01/biblia-visual.md)** segue os closes que o usuário elogiou: Kael com cabelo escuro volumoso, tecido vinho rasgado e ombreira metálica; Elara loira, olhos violeta e vestido branco-violeta com ornamentos dourados. A **[v1 original foi arquivada](videos/mmorpg-conquiste-a-princesa-ep01/biblia-visual-v1-arquivada.md)** sem apagar os 71 PNGs ou as 14 imagens-mãe antigas.

- [Manifesto SHA das duas imagens aprovadas como estética](videos/mmorpg-conquiste-a-princesa-ep01/referencias-cinematograficas-aprovadas-no-chat.json)
- [Estado do armazenamento dos PNGs originais](videos/mmorpg-conquiste-a-princesa-ep01/qa-referencias-chat-cinematograficas.json)
- [Workflow para verificar/importar originais do ZIP](../../.github/workflows/qa-alchemy-chat-cinematic-references.yml)
- [Candidato existente de câmera por cima do ombro C12-P02](videos/mmorpg-conquiste-a-princesa-ep01/candidato-camera-c12-p02.json) — ainda não aprovado para o plano

**Arquivos originais ainda pendentes no GitHub.** O pacote de dois PNGs pode ser colocado em uploads/alchemy-ep01-refs-estilo.zip para importação automática após conferir hash; isso **não** libera geração, rig nem YouTube. Exibir as referências ao usuário diretamente no chat sempre que estiverem disponíveis.

**Resolução nativa e proteção de closes:** o compositor agora suporta fotos 941×1672 e as mães antigas 1024×1536 sem esticar personagens. Um quadro antigo 2:3 perde 80px de cada lateral ao entrar em 9:16; um close 941×1672 perde apenas 0,25px por lateral. Os olhos, rostos ou objetos focais precisam de `focal_bbox` aprovado, com validação duplicada no Python e Remotion. [Detalhes e testes](videos/mmorpg-conquiste-a-princesa-ep01/PLANO-ARTE-RIG-EP01.md). **Zero arte nova e 36 rigs visuais ainda pendentes.**

## Nova regra de quadros cinematográficos

**Atuação facial por rig:** o plano `C12-P01` ganhou [controle de pupilas 12px e pálpebras 1px](videos/mmorpg-conquiste-a-princesa-ep01/rig-olhar-kael-c12-p01.json), com cabeça e cabelo estáticos. [QA](videos/mmorpg-conquiste-a-princesa-ep01/qa-olhar-kael-c12-p01.json) aprovado no código; sprites oculares e revisão artística ainda pendentes, sem render.



No dorama **Conquiste a Princesa**, a direção do programa agora separa **37 tomadas cinematográficas**, com **12 closes de rosto/olhos, 5 planos sobre o ombro e 4 planos gerais**. O gerador suporta `--shot-id` por imagem-mãe, preservando a duração e o elenco de cada tomada. As expressões de Kael, rei e princesa são focos importantes, com HUD adicionado depois no Remotion.

- [Direção JSON dos 37 enquadramentos](videos/mmorpg-conquiste-a-princesa-ep01/direcao-cinematografica-planos.json)
- [Timeline de montagem para Remotion: 37 tomadas / 4890 quadros](videos/mmorpg-conquiste-a-princesa-ep01/timeline-cinematografica.json) — 1 abertura preta pronta, **36 planos com artes e rigs exclusivos pendentes**. Montagem de pan/zoom legado bloqueada para este episódio.
- [Guia de enquadramento e continuidade](videos/mmorpg-conquiste-a-princesa-ep01/GUIA-DIRECAO-CINEMATOGRAFICA.md)
- [Testes e hashes dos 36 prompts](videos/mmorpg-conquiste-a-princesa-ep01/qa-direcao-cinematografica.json)

**Sem imagens novas nesta implementação.** Os quadros aprovados no chat servem como referência de composição, mas o visual de figurino/cabelo diverge da bíblia antiga. Antes de produzir, incorporar os arquivos reais e resolver a identidade visual. O lock de não geração de imagens segue ativo.

## Produção em andamento: dorama MMORPG — Conquiste a Princesa

**Arte em pré-produção, sem geração de novas imagens:** o episódio tem [roteiro de 14 cenas](videos/mmorpg-conquiste-a-princesa-ep01/roteiro.md), [direção de 37 planos para rigs/Remotion](videos/mmorpg-conquiste-a-princesa-ep01/direcao-rig-remotion.json) e [plano de QA](videos/mmorpg-conquiste-a-princesa-ep01/PLANO-ARTE-RIG-EP01.md).

- [71 arquivos PNG arquivados neste canal](videos/mmorpg-conquiste-a-princesa-ep01/assets/), incluindo 14 imagens-mãe, referência de personagens, fundo reconstruído e rascunhos de recortes. A contagem verificada em 14/11/2026 é de **71 PNGs**.
- [Seleção recomendada de sprites C01](videos/mmorpg-conquiste-a-princesa-ep01/rig-selecao-artes-c01.json): Kael **alinhado à cena-mãe**, guardas com textura RGB original, lanças cruzadas originais e candidato de Aldric recortado por máscara. Nenhuma camada é considerada rig aprovada.
- [Kael alinhado e suas 12 partições](videos/mmorpg-conquiste-a-princesa-ep01/assets/cena-01/rig-drafts/kael-alinhado-partes/) substituem **para fins de pré-produção** os recortes em escala errada anteriores. A recomposição preserva os pixels visíveis, mas não resolve braços e anatomia ocultos.
- [Guardas refinados](videos/mmorpg-conquiste-a-princesa-ep01/assets/cena-01/rig-drafts/guardas-refinados/) têm versões com e sem lança (esta última possui buracos a reconstruir); [Aldric](videos/mmorpg-conquiste-a-princesa-ep01/assets/cena-01/rig-drafts/aldric-origem/) é apenas candidato devido ao contato com os braços do trono.
- [Fundo reconciliado e QA](videos/mmorpg-conquiste-a-princesa-ep01/qa-recomposicao-c01-reconciliado.json): erro médio RGB do quadro neutro caiu de 11,095 para 3,446; o candidato ainda não foi aprovado visualmente.
- [ZIP de oito imagens validado](videos/mmorpg-conquiste-a-princesa-ep01/qa-zip-8-imagens-existentes.json): todos os SHA corretos, transferência binária ao GitHub ainda pendente.
- **Regra máxima deste episódio:** [NÃO GERAR NOVAS IMAGENS](videos/mmorpg-conquiste-a-princesa-ep01/SEM-GERACAO-NOVAS-IMAGENS.lock). Seis workflows que chamariam IA de imagem respeitam esse bloqueio; scripts de máscara usam apenas pixels anteriores.
- As oito variações geradas no chat permanecem em [catálogo de importação pendente](videos/mmorpg-conquiste-a-princesa-ep01/IMAGENS-EXTERNAS-PENDENTES.json): o ZIP está na conversa, mas a transferência binária para este GitHub ainda precisa ocorrer pela [pasta de importação](videos/mmorpg-conquiste-a-princesa-ep01/uploads/).

- [Oito partes dos braços dos guardas](videos/mmorpg-conquiste-a-princesa-ep01/assets/cena-01/rig-drafts/guard-arm-parts/) e [seis partes do Rei Aldric](videos/mmorpg-conquiste-a-princesa-ep01/assets/cena-01/rig-drafts/aldric-partes/): PNGs recortados dos pixels originais, com teste de recomposição. [QA dos contatos das lanças](videos/mmorpg-conquiste-a-princesa-ep01/qa-guardas-articulacoes-c01.json) — faltam underlays, articulação real e aprovação visual.

- [Auditoria de rotação dos guardas](videos/mmorpg-conquiste-a-princesa-ep01/qa-guardas-envelope-movimento-c01.json): em ±18° faltam **2410 pixels** de silhueta no guarda esquerdo e **2462 pixels** no direito. Máscaras analisadas sem gerar imagens; movimento mantém bloqueio até underlay real.
- O veto de **não gerar imagens novas** foi implementado também nos geradores Python e entradas diretas do proxy/edição, com [testes de regressão](../../tests/test_alchemy_no_image_generation.py) aprovados.

**Ainda não há MP4 oficial, rig articulado aprovado ou publicação no YouTube.** As cenas 02 e 03 continuam visualmente reprovadas e não devem ser tratadas como artes validadas.
