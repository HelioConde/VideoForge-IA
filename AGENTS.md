# AGENTS.md — VideoForge IA (reconstrução)

## REGRA Nº 1 — Vídeos exclusivamente pelo programa VideoForge-IA no GitHub

**Todo vídeo solicitado como produção oficial deve ser criado pelo fluxo de produção do repositório [HelioConde/VideoForge-IA](https://github.com/HelioConde/VideoForge-IA), executado e rastreável no GitHub Actions.** Esta regra tem prioridade sobre qualquer exemplo, demonstração, script temporário, renderer externo ou solução improvisada.

1. Usar o **programa reutilizável do projeto**, seus modelos, agentes e etapas reais, organizados em `canal/<id>/videos/<video-id>/`. Não criar um gerador paralelo específico de um único vídeo para contornar componentes ausentes.
2. Pesquisa/roteiro → arte consistente por cena → separação de personagens e cenários em camadas → animação → narração → edição/legendas → QA técnico e visual. Executar cada etapa disponível e registrar as que ainda faltam. **Não simular agentes ou artes como se tivessem sido gerados.**
3. Gerar MP4 no runner do GitHub Actions do próprio repositório; registrar workflow, run ID, commit, entrada, manifesto por canal, SHA-256, artefato e relatórios de QA. Baixar ou mostrar a cópia do MP4 é permitido, mas **não** criar/substituir a produção fora do programa.
4. Se faltarem agentes, imagens ou integração do fluxo principal, **parar como `assets_pendentes` / `pipeline_pendente` e explicar a limitação**. Não substituir por desenho vetorial, cartões ou narração sintética genérica e apresentar o resultado como o vídeo oficial solicitado. Previews experimentais podem existir para testar motores, sempre marcadas claramente como **`preview_tecnico_nao_oficial`**.
5. Apenas uma execução verificável do fluxo principal, com materiais realmente gerados e verificados, pode receber o rótulo `video_oficial_do_programa=true`. Render bem-sucedido no GitHub, por si só, **não significa** produção completa pelos agentes.
6. **Sem limite artificial para quantidade de cenas**. Segurança, licenças, orçamento aprovado, duração e QA permanecem obrigatórios. Publicação no YouTube exige autorização e verificação próprias.

**Correção histórica:** o teste *Spy x Family* da execução [43545398967](https://github.com/HelioConde/VideoForge-IA/actions/runs/43545398967) foi renderizado pelo GitHub Actions, mas usou `videoforge.spy_family_animated` e desenhos vetoriais de prévia, **não** o fluxo oficial completo de artes/agentes. É um teste técnico, não produção oficial do VideoForge-IA.

## Instruções obrigatórias para cada tarefa

**Ler nesta ordem, antes de pesquisar ou produzir qualquer vídeo:** `README.md`, `AGENTS.md`, `docs/ARQUITETURA.md`, `docs/REGRAS-EDITORIAIS.md`, `canal/README.md`, `canal/<id>/README.md`, **`canal/<id>/ESTRATEGIA.md`**, `canal/<id>/canal.json`, histórico e reservas do canal e, se útil, `docs/referencias/CATALOGO-CURSOS-YOUTUBE.md` e `docs/referencias/GUIA-OFICIAL-YOUTUBE-CREATORS.md` (para pesquisa, Analytics, SEO, Shorts, direitos, classificação infantil e IA) e **`docs/CODEX-PROXY-ACTIONS.md` antes de qualquer trabalho envolvendo ferramentas de IA, Go ou Actions**.

**Hierarquia com precedência:** a estrutura canônica é **`canal/` no singular**, conforme `docs/ARQUITETURA.md`. Não criar `canais/` alternativo. Separar rigorosamente canais; dados do vídeo em `canal/<id>/videos/<video-id>/editorial.json`, manifesto renderizável em `video.json`, índice de histórico em `canal/<id>/editorial/historico-videos.json`. Não substituir o formato técnico do manifesto. Conferir histórico e temas relacionados antes de criar nova pauta. Não presumir que o índice inicial vazio comprova ausência de vídeos no YouTube.

Ler `docs/referencias/GUIA-OFICIAL-YOUTUBE-CREATORS.md` como síntese **de fontes oficiais consultadas**, e revalidar os links originais quando decisões envolverem regras atuais. Antes de qualquer publicação futura, checar duração e Content ID em Shorts de mais de um minuto, originalidade contra conteúdo massificado/repetitivo, direitos, classificação infantil e eventual obrigação de declarar uso de IA. Nenhuma dessas instruções habilita publicação no MVP.

Os cursos listados são **fontes sugeridas para estudo**, não prova de acesso, aprendizado ou método validado. Não inventar conteúdo das aulas. Não registrar geração, QA ou publicação sem evidências.

## Integração central com Codex Proxy\n\nTodas as integrações futuras de pesquisa, roteirização e imagens devem usar o gateway definido em `docs/CODEX-PROXY-ACTIONS.md`, sem instalar Go ou clonar o upstream em cada workflow. A imagem do proxy é compilada uma vez em build isolado no GHCR; jobs posteriores usam serviço persistente ou contêiner pré-compilado. O modo efêmero não persiste tokens OAuth renovados, logo não é a opção principal. Nunca imprimir ou versionar `CODEX_PROXY_ACCOUNTS_JSON`, `CODEX_PROXY_API_KEY` ou `CODEX_PROXY_BASE_URL` privado; credenciais somente via GitHub Actions Secrets. Não habilitar geração paga em push/PR; `health` não gera imagens e `generate` é disparo manual único. Se upstream privado mudar, falhar com erro verificável, jamais tentar contornar limites 429. Geração não equivale a aprovação visual nem MP4.\n\n## Autenticação do projeto antigo: migração local

A cópia antiga usa o Environment `proxy-runtime`, mas os valores de Secrets não podem ser recuperados por API. O script `scripts/migrar-codex-proxy.ps1`, para uso **local no Windows**, importa o `accounts.json` existente no Docker ou em arquivo privado e registra os novos Secrets via stdin no `gh` CLI. Nunca armazenar tokens, senhas, chaves, dumps ou arquivos de conta em commits, logs, discussões, PRs, artifacts ou GitHub Pages. Não afirmar que houve migração até ela ser executada localmente e verificada em Actions. Consulte `docs/CODEX-PROXY-ACTIONS.md`.

## Testes de separacao generativa por camadas

Antes de modificar ou executar rotinas de edicao de cenas, leia `docs/TESTE-CAMADAS-CENA.md`. Os workflows `scene-layers-basic.yml` e `scene-layers-advanced.yml` executam somente por `workflow_dispatch`, reutilizam o mesmo PNG original verificado por hash, usam o proxy Go PRECOMPILADO e limitam no maximo 2 imagens por run, sem retry automatico. Resultados vao exclusivamente para `output/<canal>/videos/<video-id>/assets/<cena>/` como artifacts; nunca sao versionados, enviados ao YouTube ou classificados como animacao pronta. O manifesto tem `human_visual_approval=false`, `pixel_alignment_verified=false` e `animation_implemented=false` ate verificacao adequada. Uma edicao por IA NAO e recorte fiel e nao pode substituir QA humano.

## Prévia de animação de camadas verificável

O workflow manual `animate-separated-layers.yml` consome somente o artifact do Teste 2, sem chamadas ao proxy, sem reinstalação de Go/FFmpeg e sem upload ao YouTube. O motor `videoforge/animate_layers.py` anima 3 camadas independentes via FFmpeg, verifica SHA-256, RGBA real, movimento entre quadros e codecs do MP4. A capa e demais peças que ainda existem no personagem-base **não podem ser adicionadas como overlays**, pois isso duplicaria roupa/objetos. É obrigatório criar personagem-base sem a peça e pivôs revistos antes do rig. `modelos/camadas-animadas` permanece desabilitado para produção completa. Ver `docs/ANIMACAO-CAMADAS.md`.

## Motor Remotion reaproveitado do projeto antigo

Para prévias animadas de PNGs, usar como **primeira escolha** a composição React em `motion-remotion/src/scene-layer-preview.tsx` e o [guia](docs/REMOTION-ANIMACAO.md). Os módulos `character-idle.ts`, `cinematic-motion.ts` vieram do `AutoEditorVideo/motion-remotion` fixado em `ec85db5bc74455122e4501aba05bd2dd3fd0df2c`, e `videoforge-motion.ts` do antigo VideoForge. A renderização é executada no workflow `remotion-animate-layers.yml` usando imagem GHCR de Node/Remotion/Chrome já compilada, sem npm ci ou download do navegador a cada job. FFmpeg somente gera silêncio e verifica codecs/quadros. Validar SHA, RGBA e identidade do canal antes de compor, **não duplicar a capa**, não fingir rig de membros/cabelo, não enviar ao YouTube. Modelo `camadas-animadas` ainda não é produção pronta.

## Rig 2D de malha (opt-in, nao aprovado para producao)

Ler [docs/RIG-MALHA-2D.md](docs/RIG-MALHA-2D.md) antes de preparar sprites ou alterar `motion-remotion/src/mesh-rig.tsx`. O rig SVG so pode ser ativado com cinco sprites RGBA sem partes duplicadas, hashes vinculados a cena e `human_review` verdadeiro **apos** revisao real. Nao usar `character-main.png` no mesmo modo de render que `body-no-head-no-cape.png` e `cape.png`. Validacao automatica nao prova qualidade visual; manter `publishable=false` e `visual_review=pending` ate revisar MP4. A existencia de codigo nao significa que os PNGs ou o artifact de rig ja existam. Nao executar inferencia IA nem upload por conta propria.

## Preparacao do rig candidato por cena (sem aprovacao automatica)

Consultar [docs/PREPARAR-RIG-CANDIDATO.md](docs/PREPARAR-RIG-CANDIDATO.md) e `canal/<id>/videos/<video-id>/rig-plan.json` antes de alterar máscaras. `videoforge/rig_candidate.py` **nao** executa SAM2/LaMa nem reconstrói anatomia escondida; apenas gera recortes e previews de risco. Na cena piloto o desenho inclui **segundo olho parcialmente visível** e capa frontal/traseira; separar as partes evita duplicações. Sempre manter `human_review=false` no rascunho; não renomear seu artifact para `rig-...` nem alimentar o workflow de MP4 final sem correção de arte, checagem de oclusão e aprovação humana. O workflow `rig-candidate.yml` não chama API de IA nem publica vídeos.

## Regra permanente — não limitar cenas por número

Nunca acrescentar `MAX_SCENES`, faixas como `3 <= len(scenes) <= 24`, ou checagens exigindo exatamente 10 cenas nos geradores de vídeo. O número de cenas é consequência do **roteiro e dos cortes visuais necessários**, não um teto arbitrário. Validar que a lista é não vazia, caminhos e conteúdo de cada cena, direitos, tempo final do formato, QA e uso de recursos; jamais truncar ou descartar cenas automaticamente para caber em número máximo. Dividir trabalhos em lotes técnicos quando necessário preservando a ordem e o conteúdo, sem limitar o número total de cenas. Orçamento de geração de imagens, quotas de APIs, timeout e limites de duração do Shorts permanecem controles separados e não podem ser burlados.

## Padrão universal da animação de personagens

Antes de desenhar, separar sprites, montar rig ou renderizar personagens de **qualquer canal**, leia [`docs/PADRAO-ANIMACAO-POR-CAMADAS.md`](docs/PADRAO-ANIMACAO-POR-CAMADAS.md). A regra geral é: base do rosto sempre opaca durante a piscada; cabelo e roupas separados apenas quando houver underlay e sobreposição nas costuras; junções ancoradas nos ombros/pescoço; movimento determinístico de corpo, cabelo, roupa e câmera sem fendas, duplicação ou esticar a cabeça. Todo vídeo exige continuidade entre cenas, QA de quadros e aprovação visual. A prévia vetorial de Spy x Family prova apenas o motor: **não** tratá-la como ilustração final ou publicação.

## Objetivo inicial

**No MVP técnico**, comprovar MP4 vertical do Otaku Multicena com 90–180 segundos, áudio audível e QA. **Na produção oficial**, usar exclusivamente o programa integrado no GitHub, com agentes/etapas reais, ilustrações e mídia comprovadas. Validar o renderizador não equivale a gerar vídeo final pelo programa.

## Regras de execução

- O comando smoke usa mídia sintética para testar tecnologia; **jamais**
  registrar esse clipe como produção realizada por agentes.
- O comando render só usa mídia real explicitamente fornecida;
  não inventar identidade de personagem, fontes ou artefatos.
- Sem upload para YouTube e sem chamadas pagas de IA nesta etapa.
- Jamais adicionar credenciais, respostas privadas, imagens geradas,
  áudio de produção ou MP4s ao Git.
- Registrar origem, orçamento e autorização antes de integrar provedores
  de imagem, voz ou pesquisa; não contornar 429 com repetição cega.
- Manter QA fail-closed; qualquer falha de áudio, duração, resolução
  ou integridade bloqueia declaração de vídeo concluído.
- Alterar código em branch/PR e verificar CI antes de integrar.
- Não tocar no repositório antigo. Organizar arquivos por canal,
  preservar documentação e não introduzir agentes visuais fictícios.

## Regra de execução sem instalações repetidas

Os workflows de produção devem reutilizar imagens GHCR pré-compiladas. Usar `ghcr.io/helioconde/videoforge-media-runner:ubuntu2404-ffmpeg-v2` para renderização e o proxy pinado do `docs/CODEX-PROXY-ACTIONS.md` para IA. Nunca reinstalar Go, FFmpeg ou serviços em cada job de vídeo; builds/atualizações são feitos só nos workflows de infraestrutura, com cache e tags estáveis. Runners hospedados ainda precisam baixar a imagem, pois não persistem disco entre execuções. Toda troca de imagem exige smoke real H.264/AAC com QA.

## Validação

    python -m unittest discover -s tests -v
    python -m videoforge.mvp smoke --output dist/smoke.mp4

Conferir artefato de Actions: video H.264, áudio AAC, 1080 × 1920 e QA JSON.
Esse teste não autoriza vídeo público nem consumo de IA.

## Organização permanente — mesmo contrato do VideoForge anterior

Sempre consultar `README.md`, `docs/ARQUITETURA.md` e
`docs/ESTRATEGIA_SHORTS.md` antes de editar ou planejar Shorts.
O guia de Shorts é orientação **editorial**, não autorização para novos jobs,
provedores pagos, pesquisa privada ou publicação.
A estrutura do repositório anterior `HelioConde/video-forge-ia2` é a
referência **apenas para organização**, sem copiar credenciais, pipelines
complexos nem trabalhos fictícios.

- Cada canal vive exclusivamente em `canal/<id>/`; seus dados não podem
  migrar nem ser misturados com os de outro canal.
- Em `canal/<id>/`, manter `canal.json`, `README.md`, 
  `conteudos/indice.json`, `editorial/candidatos.json`,
  `editorial/reservas.json` e `videos/README.md`.
- Pesquisas com fontes ficam em `editorial/pesquisas/YYYY-MM-DD.json`.
  Pastas de arquivo editorial têm valor histórico, **não são fila de produção**.
- Cada vídeo real usa `canal/<id>/videos/<video-id>/video.json`. O modelo
  técnico padrão vem de `canal.json.modelo_padrao`, com sobrescrita opcional
  em `video.json.modelo`; modelos reutilizáveis em `modelos/<id>/modelo.json`.
- Geradores específicos de nicho podem viver em `geradores/<id>/` somente
  quando houver implementação e testes reais; não inferir trabalho ativo a
  partir de arquivos de configuração.
- Manter resultados e dados temporários em `output/<id>/editorial/` ou
  `output/<id>/videos/<video-id>/`, nunca versionados.
- O MVP só processa `otaku-br` e `imagem-estatica` fornecida. O modelo
  `camadas-animadas` está **planejado, não implementado**. 
- `videoforge/paths.py` deve falhar antes de gerar mídia se o canal,
  diretório, receita técnica ou destino de saída estiverem incorretos.
- Em toda mudança: organizar antes e depois, atualizar docs,
  testar regressões, verificar Actions; nunca editar outros repositórios,
  gastar IA ou publicar YouTube sem autorização explícita.

## Diagnosticar rig sem aprovar sprites

Para ver movimento antes de reconstruir partes ocultas, o workflow `rig-draft-preview.yml` produz MP4 **com marca d'água de rascunho** e quadros de revisão. O módulo `videoforge/rig_draft_preview.py` deve aceitar somente `rig-candidate` com `human_review=false`, SHA validado e origem/canal corretos; nunca converter rascunho em aprovação ou publicar o vídeo. Marcar `publishable=false` e registrar inpainting pendente no QA. A versão de produção segue exigindo `validate_rig_dir` com aprovação visual humana.
