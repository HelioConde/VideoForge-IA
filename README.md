# VideoForge IA — reconstrução orientada a MP4

> **MANUAL PRINCIPAL DE ANIMAÇÃO 2D (OBRIGATÓRIO PARA TODOS OS CANAIS):** [Leia primeiro o manual de malha Three.js + Remotion](docs/MANUAL-PRINCIPAL-ANIMACAO-2D.md). Ele tem prioridade sobre regras antigas de bob/câmera/pálpebras em overlay. Nenhuma animação oficial deve ser classificada como rig articulado quando apenas o PNG inteiro se move. Exigir cena-mãe, partes RGBA independentes, reconstrução de regiões ocultas, rig por pivôs/malhas, comparação com arte original, QA e aprovação. **Sem sprites reais completos, manter como pipeline pendente.**

> **LEITURA OBRIGATÓRIA (antes de qualquer tarefa):** [AGENTS.md](AGENTS.md) → [Arquitetura das pastas](docs/ARQUITETURA.md) → [Regras editoriais dos vídeos](docs/REGRAS-EDITORIAIS.md) → [Regras do canal](canal/README.md) → **[Estratégia específica do canal](canal/README.md#estratégias-específicas-por-canal) e `canal/<id>/ESTRATEGIA.md`** → [Cursos de referência](docs/referencias/CATALOGO-CURSOS-YOUTUBE.md) → [Guia oficial YouTube Creators](docs/referencias/GUIA-OFICIAL-YOUTUBE-CREATORS.md) → [Infraestrutura Codex Proxy](docs/CODEX-PROXY-ACTIONS.md).
>
> **Prioridade absoluta:** preservar a estrutura existente **`canal/<id>/`** (singular), `modelos/`, `geradores/`, `videoforge/`, `tests/` e `docs/`. Cada vídeo tem seus dados e histórico dentro de seu próprio canal; não criar `canais/` nem misturar informações entre canais. Cursos de YouTube são **referências para estudo**, não aulas já assistidas. A análise oficial do YouTube Creators está registrada com fontes e ressalvas; políticas devem ser revalidadas antes de publicar.
>
> Esta organização mantém o MVP apenas como **teste técnico**. Vídeo oficial exige o fluxo real e integrado do programa (agentes, arte, animação, voz, edição, QA e proveniência no GitHub); nenhuma prévia substitui essa integração. Sem publicação automática ou IA paga nesta etapa.

## Regra nº 1 — Vídeos exclusivamente pelo programa VideoForge-IA no GitHub

**Todo vídeo solicitado como produção oficial deve ser criado pelo fluxo de produção do repositório [HelioConde/VideoForge-IA](https://github.com/HelioConde/VideoForge-IA), executado e rastreável no GitHub Actions.** Esta regra tem prioridade sobre qualquer exemplo, demonstração, script temporário, renderer externo ou solução improvisada.

1. Usar o **programa reutilizável do projeto**, seus modelos, agentes e etapas reais, organizados em `canal/<id>/videos/<video-id>/`. Não criar um gerador paralelo específico de um único vídeo para contornar componentes ausentes.
2. Pesquisa/roteiro → arte consistente por cena → separação de personagens e cenários em camadas → animação → narração → edição/legendas → QA técnico e visual. Executar cada etapa disponível e registrar as que ainda faltam. **Não simular agentes ou artes como se tivessem sido gerados.**
3. Gerar MP4 no runner do GitHub Actions do próprio repositório; registrar workflow, run ID, commit, entrada, manifesto por canal, SHA-256, artefato e relatórios de QA. Baixar ou mostrar a cópia do MP4 é permitido, mas **não** criar/substituir a produção fora do programa.
4. Se faltarem agentes, imagens ou integração do fluxo principal, **parar como `assets_pendentes` / `pipeline_pendente` e explicar a limitação**. Não substituir por desenho vetorial, cartões ou narração sintética genérica e apresentar o resultado como o vídeo oficial solicitado. Previews experimentais podem existir para testar motores, sempre marcadas claramente como **`preview_tecnico_nao_oficial`**.
5. Apenas uma execução verificável do fluxo principal, com materiais realmente gerados e verificados, pode receber o rótulo `video_oficial_do_programa=true`. Render bem-sucedido no GitHub, por si só, **não significa** produção completa pelos agentes.
6. **Sem limite artificial para quantidade de cenas**. Segurança, licenças, orçamento aprovado, duração e QA permanecem obrigatórios. Publicação no YouTube exige autorização e verificação próprias.

**Correção histórica:** o teste *Spy x Family* da execução [43545398967](https://github.com/HelioConde/VideoForge-IA/actions/runs/43545398967) foi renderizado pelo GitHub Actions, mas usou `videoforge.spy_family_animated` e desenhos vetoriais de prévia, **não** o fluxo oficial completo de artes/agentes. É um teste técnico, não produção oficial do VideoForge-IA.

**Estado atual:** há renderizadores de testes técnicos, mas a produção oficial ainda exige integrar pesquisa, agentes, modelos de imagem, animação, voz e QA ao fluxo principal. Não classificar MP4 experimental como trabalho concluído do gerador. O repositório
anterior, agora `HelioConde/video-forge-ia2`, permanece intacto e serve
somente como referência para organização.

## Estratégia editorial de Shorts

Os materiais de crescimento/SEO enviados em 2026-11-13 foram sintetizados
em [Estratégia de YouTube Shorts](docs/ESTRATEGIA_SHORTS.md), que inclui
pesquisa, antirrepetição por canal, retenção, consistência visual,
métricas e fontes oficiais atualizadas. **Leia o guia antes de planejar**;
essas práticas ainda não são automações implementadas.

## Infraestrutura IA: Codex Proxy e Actions\n\nO componente central planejado de IA é [10/chatgpt-codex-proxy](https://github.com/10/chatgpt-codex-proxy). Os workflows manuais [build de imagem do proxy](.github/workflows/proxy-image.yml) e [teste/geração de imagem](.github/workflows/proxy-images.yml) usam imagem Docker precompilada ou um serviço HTTPS com sessão persistente, sem reinstalar Go em todo job. **Confira o passo a passo de secrets e os limites** em [docs/CODEX-PROXY-ACTIONS.md](docs/CODEX-PROXY-ACTIONS.md). Esta infraestrutura não significa que credenciais já foram configuradas, imagem foi gerada ou publicação foi habilitada.\n\n## Ferramentas de mídia reutilizadas nos workflows

O workflow [MVP MP4](.github/workflows/mvp.yml) usa a imagem pré-compilada `ghcr.io/helioconde/videoforge-media-runner:ubuntu2404-ffmpeg-v2`, com Python 3.12, FFmpeg 6.x e fontes. O build fica isolado em [media-image.yml](.github/workflows/media-image.yml); cada job faz apenas pull da imagem, **não** reinstala Go, Python ou FFmpeg. O Codex Proxy tem sua imagem separada.

## Aproveitar as contas do Codex Proxy anterior

Para migrar a sessão já autorizada do contêiner Docker antigo sem novo login no Codex, o [script local de migração](scripts/migrar-codex-proxy.ps1) envia o estado privado aos Secrets do novo repositório pelo `gh` CLI. Consulte [as instruções e limitações](docs/CODEX-PROXY-ACTIONS.md). Secrets antigos do GitHub não podem ser lidos de volta pela API.

## Testes de decomposicao de cena com IA (separados do MVP)

Os workflows [Teste 1 - background e personagem](.github/workflows/scene-layers-basic.yml) e [Teste 2 - foreground e objetos animaveis](.github/workflows/scene-layers-advanced.yml) usam **a mesma cena-base** obtida no artifact do Codex Proxy. A geracao e manual e limitada a no maximo 2 edicoes de imagem por run; PNGs e manifesto ficam somente em artifacts organizados por canal. Consulte o [guia de testes de camadas](docs/TESTE-CAMADAS-CENA.md). A edicao e generativa: transparencia tecnica nao garante recorte fiel, coordenadas ou animacao pronta.

## Prévia animada das camadas em MP4 (sem IA)

O [Teste 3 de animação](.github/workflows/animate-separated-layers.yml) usa os PNGs de background, personagem e telhado obtidos pela separação para criar uma prévia parallax de 6–10 segundos com **movimentos independentes**. O motor `videoforge/animate_layers.py` verifica o artifact, renderiza H.264/AAC e confere movimento real entre quadros. **A capa isolada ainda não é usada** porque permanece dentro do sprite completo e seria duplicada; o vídeo é técnico, sem narração e sem envio ao YouTube. [Instruções](docs/ANIMACAO-CAMADAS.md).

## Remotion original — nova prévia animada por camadas

O motor **principal para a nova prévia** é agora [Remotion do AutoEditorVideo](motion-remotion/): reutilizamos as funções do projeto anterior em uma composição React que movimenta camera, personagem e foreground por frame. O novo [workflow manual Remotion](.github/workflows/remotion-animate-layers.yml) usa os PNGs dos artifacts reais com validação de SHA-256, renderiza MP4 com H.264/AAC e QA de movimento, **sem gastar IA ou instalar npm/Chrome toda vez**. Consulte [guia do Remotion](docs/REMOTION-ANIMACAO.md). O renderizador antigo de parallax FFmpeg permanece somente como teste/fallback documentado; a capa não é sobreposta até remover sua versão duplicada do personagem.

## Preparacao visual do rig com pixels da cena original (rascunho)

A nova etapa de [preparação dos sprites](docs/PREPARAR-RIG-CANDIDATO.md) usa o artifact original verificado para produzir **seis camadas candidatas**, separando a capa em frente e trás e reconhecendo os dois olhos parcialmente visíveis. O workflow `rig-candidate.yml` gera máscaras, contact sheet, hashes e proveniência **sem IA e sem publicar**. Os recortes ainda não reconstroem anatomia escondida e permanecem bloqueados para uso como rig aprovado.

## Rig 2D por malha — implementacao opt-in (ainda sem sprites aprovados)

O novo [MVP de rig 2D](docs/RIG-MALHA-2D.md) acrescenta ao Remotion um **warp por triangulos da capa**, **pivo da cabeca no pescoco** e **piscadas em quadros definidos**. O codigo e validadores existem; a ativacao depende de cinco PNGs RGBA sem partes duplicadas, hashes e revisao visual humana. Sem rig, o workflow permanece no modo legado; **nao existe ainda MP4 real aprovado deste modo novo**. Nao habilita publicacao nem o modelo `camadas-animadas` para producao.

## Regra permanente: sem teto de quantidade de cenas

**O gerador não deve impor limite fixo de cenas** (nem 10, 24, 30 ou outro valor arbitrário). Roteiros, manifestos e renderizadores devem aceitar qualquer número **positivo** de cenas válido, determinado pela narrativa. O motor renderiza e valida cena a cena, sem reduzir, mesclar, cortar ou descartar cenas apenas por terem ultrapassado uma contagem pré-definida.

Esta regra não remove o QA, a exigência de assets reais, as verificações de direitos, a segurança contra abuso, o orçamento autorizado de IA, os limites operacionais do GitHub Actions nem a **duração** do formato. Por enquanto o piloto Shorts do Otaku BR permanece com 90–180 segundos; se a narrativa não couber, deve ser adaptada ou planejada para formato mais longo, não ter cenas apagadas automaticamente. Mudanças no número de cenas não significam publicação ou geração de IA automática.

## O que já funciona

- Compositor FFmpeg de **imagens e narrações fornecidas**, com legendas,
  MP4 H.264/AAC vertical 1080 × 1920.
- QA automático de vídeo, áudio, duração, resolução e SHA-256.
- Smoke test no GitHub Actions produz clipe técnico sintético de ~5 segundos
  (não é vídeo editorial, não é produção de agentes, sem IA paga).
- Produção do primeiro Otaku Multicena exige **90–180 segundos**
  e a autorização humana para qualquer integração futura de IA.
- Não há publicação no YouTube, nem credenciais no Git.

## Pastas — igual ao VideoForge anterior

```text
canal/
  otaku-br/                         # Otaku Multicena, piloto
    canal.json                      # opções / modelo padrão
    conteudos/indice.json           # referências, não fila automática
    editorial/
      candidatos.json               # pesquisas autenticadas futuras
      reservas.json                 # antirrepetição, começa vazio
      pesquisas/YYYY-MM-DD.json     # futuro, só pesquisa verificável
    videos/
      <video-id>/video.json         # manifesto por vídeo
  otaku-en/                         # Otaku Reframe
  gamer/                            # Conde Games
  manu-kids/                        # Emanuelly Kids
  alchemy-lab/                      # Alchemy Lab
modelos/
  imagem-estatica/modelo.json       # implementado: imagens fornecidas
  camadas-animadas/modelo.json      # PLANEJADO, ainda não implementado
geradores/                          # receitas de nicho futuras
videoforge/                         # código reutilizável
tests/                              # testes offline e FFmpeg
docs/ARQUITETURA.md                 # regra permanente de organização
output/
  <channel>/videos/<video-id>/      # MP4 e QA; ignorado pelo Git
```

Confira [regras dos canais](canal/README.md),
[modelos](modelos/README.md) e
[arquitetura](docs/ARQUITETURA.md).

**Isolamento:** nenhum vídeo, métrica, pauta ou reserva de um canal pode ser
usado como se fosse de outro. O código valida canal e modelo, e bloqueia
o destino de saída fora de seu diretório.

## Executar

Requer Python 3.12+ e FFmpeg/FFprobe no PATH, sem dependências Python extras.

```bash
python -m unittest discover -s tests -v
python -m videoforge.mvp smoke --output dist/smoke.mp4
```

Após fornecer **mídia realmente existente** e o manifesto aprovado:

```bash
python -m videoforge.mvp render --video canal/otaku-br/videos/episodio-001/video.json
```

Esse comando gera o arquivo e relatório QA em:
`output/otaku-br/videos/episodio-001/video.mp4` e
`output/otaku-br/videos/episodio-001/video.qa.json`.

O manifesto `video.json` tem este formato **ilustrativo**:

```json
{
  "schema": "videoforge/mvp/v1",
  "channel": "otaku-br",
  "modelo": "imagem-estatica",
  "youtube_upload": false,
  "scenes": [
    {"image": "imagens/cena-01.png", "audio": "voz/cena-01.mp3", "caption": "Legenda 1"},
    {"image": "imagens/cena-02.png", "audio": "voz/cena-02.mp3", "caption": "Legenda 2"},
    {"image": "imagens/cena-03.png", "audio": "voz/cena-03.mp3", "caption": "Legenda 3"}
  ]
}
```

Os arquivos de imagens e voz devem existir ao lado de `video.json` nos
respectivos subdiretórios, mas **não são versionados**. A narração somada
precisa durar 90–180 segundos. O manifesto de exemplo **não contém mídia
nem aprova a escolha do tema**.

`modelo` é opcional no vídeo e usa por padrão `canal.json.modelo_padrao`.
O Otaku Multicena tinha `camadas-animadas` como padrão provisório no antigo
projeto; nesta reconstrução usa `imagem-estatica` **temporariamente** para
entregar um MP4 real primeiro. O modelo de camadas ainda está desativado.

## Próximos marcos

1. Preservar o MP4 técnico aprovado pelo CI após organização por canal.
2. Renderizar vídeo de 90–180s com áudio e imagens reais, sem falar em
   agentes até haver evidências dos trabalhos deles.
3. Só depois implementar pesquisa, três agentes independentes,
   provedores de IA com limites, identidade visual e animações.
4. YouTube Analytics, QA editorial e publicação são etapas separadas;
   nunca enviar conteúdo automaticamente.

**QA técnico não é aprovação editorial ou visual.**
