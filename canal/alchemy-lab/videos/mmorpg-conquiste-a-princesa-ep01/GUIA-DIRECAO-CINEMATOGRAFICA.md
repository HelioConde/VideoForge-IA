# A Missão Impossível — enquadramentos cinematográficos do EP01

**Implementação:** [37 planos em JSON](direcao-cinematografica-planos.json) lidos por `videoforge/cinematic_direction.py` e integrados a `videoforge/production_scenes.py` com `--shot-id`.  
**Estado:** planejamento e prompts prontos, geração de novas imagens bloqueada, rigs e MP4 oficial pendentes.

## Como ficam os quadros do episódio

| Plano | Visão da câmera | O que a pessoa deve sentir |
|---|---|---|
| C01-P01 | Tela totalmente preta, sem imagem | Silêncio e expectativa |
| C01-P02 | Insert de mão, bainha e espada sendo desembainhada | Ameaça iminente |
| C01-P03 | Ângulo baixo de Kael ajoelhado diante do enorme trono | Vulnerabilidade |
| C01-P04 | Único plano geral com rei e dois guardas cruzando lanças | O poder da corte |
| C02-P01 | **Close do rosto do rei Aldric**, trono desfocado | Autoridade e julgamento |
| C02-P02 | **Close de Kael com cabeça baixa**, tensão na expressão | Medo contido |
| C03-P01 | **Extremo close dos olhos de Kael**, reflexo azul | Memória e ruptura |
| C07-P03 | Plano a dois, Elara pedindo ajuda a Kael | Confiança inesperada |
| C09-P01 | **Close de Elara agradecendo**, mão em contato | Emoção cautelosa |
| C12-P01 | **Extremo close dos olhos de Kael**, somente pupilas se movem | Reconhecimento secreto |
| C12-P02 | Câmera sobre ombro de Kael revela princesa ao lado do trono | Revelação |
| C12-P03 | **Close de reação de Elara**, flor prateada visível | Surpresa |
| C14-P02 | **Close do rosto da princesa** declarando noivado | Decisão e coragem |
| C14-P03 | **Extremo close dos olhos de Kael**, corte para preto | Gancho final |

Os demais 23 planos estão documentados individualmente no JSON. **Não reaproveitar o plano geral como imagem para todos os closes.** Um close cinematográfico exige sua própria imagem-mãe e sua própria extração de sprites/fundo da mesma ilustração quando houver autorização.

## Fotos de referência recentes do chat

O usuário aprovou a direção visual com close dramático de Kael (cabelo escuro desalinhado, marcas no rosto, lenço/capa vermelha e ombreira de armadura), plano sobre o ombro e close de reação da princesa (cabelo loiro e vestido branco/violeta) com rei e salão desfocados. Essas imagens servem como **exemplo de enquadramento e atuação**, não como PNGs que já estejam arquivados no GitHub.

**ATENÇÃO — conflito de identidade:** a bíblia antiga deste episódio descreve Kael **sem capa/armadura** e Elara **de cabelo preto/vestido azul**. Se misturar as descrições, o vídeo ficará incoerente. Os próximos renders precisam de **uma versão visual definitiva** antes da produção: importar as imagens de referência aprovadas no canal, validar continuidade, substituir as descrições antigas de maneira consciente e registrar SHA. A implementação agora bloqueia novas gerações se essa divergência não tiver sido resolvida, além do bloqueio já solicitado `SEM-GERACAO-NOVAS-IMAGENS.lock`.

## Contrato do gerador (por tomada)

`python -m videoforge.cinematic_direction --channel alchemy-lab --video-id mmorpg-conquiste-a-princesa-ep01 --shot-id C12-P01`

Esse comando somente **mostra o prompt do close**. Não gera imagem, não chama o proxy nem publica nada. Para conferir todos os 37 enquadramentos, omitir `--shot-id`.

A interface de geração futura `videoforge.production_scenes` recebe opcionalmente `--shot-id C12-P01`, e o workflow `.github/workflows/production-scene-by-request.yml` ganhou o mesmo campo. As 14 imagens-mãe antigas não são apagadas; os planos específicos terão IDs independentes quando houver autorização, por exemplo `cena-12-c12-p01.png`. A primeira tomada `C01-P01` é preto absoluto e é impossível solicitar arte para ela.

**HUD e texto:** nunca desenhar títulos, missões ou caixas de texto dentro da arte. O primeiro título pode aparecer como elemento da montagem, e o restante do HUD de MMORPG deve entrar somente como camada do Remotion nos planos que o roteiro pedir.

**Rig real:** o novo close precisa de cabeça aberta/fechada, olhos, franja/cabelo, partes de corpo, alfa e underlay próprios do mesmo quadro e QA antes de ser animado. Movimento de câmera não substitui os rigs (manual principal mantém prioridade).

## Auditoria

A execução GitHub Actions `43637493536` aprovou a integridade dos 37 planos, o elenco, a variedade cinematográfica e a preparação de 36 prompts. O relatório em [qa-direcao-cinematografica.json](qa-direcao-cinematografica.json) contém SHA-256 dos 36 textos.

**Estado final da solicitação:** zero novas imagens, zero MP4, zero upload ao YouTube; planejamento do programa implementado e prontidão de referência/arte aguardando revisão.


## Timeline de edição real do programa (EDL)

O programa agora usa [timeline-cinematografica.json](timeline-cinematografica.json), construído por `videoforge/cinematic_shot_assets.py`. Esse documento conecta cada `CXX-PXX` aos frames absolutos para edição **sem transições falsas**: 37 planos contínuos entre frames 0 e 4890 a 30fps, total de 163 segundos. O primeiro plano `C01-P01` é preto e não precisa de arte.

As **36 tomadas com imagem** têm diretórios individuais em `assets/planos/CXX-PXX/`. Dentro de cada diretório, o contrato exigirá a mãe `scene-mother.png`, `background-reconstructed.png`, `rig.json` com PNGs RGBA independentes de corpo/cabeça/olhos/mãos/cabelo e `qa.json` com prova de origem, pivôs, underlays, composição neutra, identidade e revisão visual. As artes já existentes dos 14 cenários **não substituem** automaticamente essas tomadas. Nenhum desses 36 planos foi aprovado para render.

A regra de segurança foi aplicada também a `videoforge/production_assemble.py`: o render técnico legado de imagem inteira com movimento `cinematic-pan` é **bloqueado para vídeos com timeline por plano**, sem alterar outros canais. O `official_production.py` informa que a cena exige rigs reais por tomada e que ainda falta a integração do renderer multi-personagem com ThreeCanvas/Remotion.

O validador da EDL impede buracos e sobreposições de frames, caminhos inseguros, SHA inválido, RGBA de outra tomada, imagens sem pivôs ou underlays, QA não aprovado e aprovação falsa. Todos os arquivos ficam na pasta do canal; o workflow apenas escreve a timeline JSON, **não gera PNG, não renderiza MP4 e não publica**.

**Atenção:** o manifesto é um contrato de montagem validado, não uma declaração de que os 36 rigs já existem. O bloqueio `SEM-GERACAO-NOVAS-IMAGENS.lock` segue ativo.


## Compositor ThreeCanvas e exportação de rigs aprovados

A montagem de 37 tomadas também ganhou um **compositor real no Remotion** em `motion-remotion/src/cinematic-episode.tsx`, que utiliza `Sequence` com cortes em frames absolutos, `ThreeCanvas` com múltiplos personagens e `CharacterParts` para movimentos independentes de cabeça/cabelo/malha. A proporção 1024×1536 da arte é ajustada à saída 1080×1920 **sem distorção de rosto**; a imagem-mãe achatada nunca é usada como animação principal. A primeira tomada é tela preta sem PNG, e o HUD é desenhado apenas como camada Remotion quando explicitamente aprovado.

A entrada foi isolada em `motion-remotion/src/cinematic-index.ts` (`VideoForgeCinematicEpisode`), preservando o player legado. O contrato `motion-remotion/src/cinematic-timeline.ts` **recusa renderizar todo o episódio** se qualquer tomada estiver sem SHA, procedência do próprio ângulo, rig corporal independente, movimento de malha, aprovação visual e UI, ou se os intervalos de frames estiverem incorretos.

O exportador `videoforge/cinematic_remotion_export.py` prepara no futuro o arquivo de props e copia para `motion-remotion/public/vf-cinema/` **apenas arquivos PNG que já existem, com SHA conferido**. Ele exige que os PNGs das partes estejam recortados de acordo com suas caixas `bbox` originais, tenham proveniência na própria imagem-mãe, underlays aprovados, rig multiator e QA. O comando abaixo é ilustrativo do **procedimento futuro**, não deve ser executado ainda:

```bash
# Só funcionará quando TODAS as 36 tomadas tiverem assets e rigs aprovados:
python -m videoforge.cinematic_remotion_export --stage
cd motion-remotion
npm run render:cinematic:official -- --props=../output/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/cinematic-render-props.json
```

Sem esses requisitos, o exportador falha antes de copiar qualquer arquivo e a composição Remotion rejeita os argumentos. **Não usar props fictícios de testes como produção!** Os testes do compositor são memórias sintéticas em tempo de teste, nunca imagens falsas arquivadas.

Testes: `npm run typecheck`, `npm run test:cinematic`, `python -m unittest tests.test_cinematic_remotion_export`. O [workflow de QA do compositor](https://github.com/HelioConde/VideoForge-IA/actions/workflows/qa-cinematic-remotion-renderer.yml) não gera imagens, não renderiza vídeo e não acessa YouTube.

**Estado atual:** o código do compositor e seu contrato de asset estão implementados e o typecheck passou; **nenhuma das 36 tomadas visuais do EDL possui pacote independente de arte+rig aprovado**, portanto o MP4 não foi produzido. Os 71 PNGs anteriores permanecem intactos em `canal/alchemy-lab`. O bloqueio de geração permanece ativo.


## Close ocular de Kael — C12-P01

O plano de reação `C12-P01` dura **120 frames** e é um exemplo obrigatório de atuação real do personagem em close. O Remotion mantém **a cabeça, a respiração do corpo, o cabelo, o manto e a câmera imóveis**. Somente as pupilas e pálpebras têm movimentos:

- Frame local 0–4: pupilas na posição neutra.
- Frames 4–86: olhar se desloca gradualmente de 0 a +12 pixels.
- Frames 86–119: olhar permanece no extremo, sem girar a cabeça.
- Pálpebras seguem o mesmo gesto com deslocamento gradual de 0 a +1 pixel após o frame 7.

O programa exige a extração de **quatro PNGs transparentes e independentes** (`pupil-left`, `pupil-right`, `eyelid-left`, `eyelid-right`), além de arte facial sem pupilas duplicadas, esclerótica reconstruída, limites oculares testados e QA humano. Sem isso, o close continuará recusado pelo renderer e pelo exportador.

[Contrato de arte ainda pendente](rig-olhar-kael-c12-p01.json) · [Testes e bloqueios](qa-olhar-kael-c12-p01.json)

**Importante:** a movimentação do código foi testada, mas ainda **não existe material visual aprovado para executar esse close**. Não gerar imagens sem uma nova autorização. Não declarar esse plano renderizado.
