# MVP de rig 2D por malha — VideoForge IA / Remotion

**Estado:** codigo opt-in implementado; **sprites articulados reais e aprovacao visual ainda pendentes**. Nao representa um video publicado nem habilita `modelos/camadas-animadas` para producao. O Remotion legado permanece o padrao quando nao ha rig.

## Por que essa abordagem

A cena atual de `otaku-br/teste-proxy-20261113/cena-01` tem `background.png`, `character-main.png`, `foreground-roof.png` e `cape.png`. A capa aparece tanto no `character-main.png` quanto no `cape.png`: simplesmente sobrepor a capa cria duplicacao. **Nao usar rig com esses sprites antigos sem nova separacao**.

O MVP usa **Remotion 4 + SVG com triangulos afins** dentro do Chromium ja instalado no runner GHCR. Cada quadro transforma os vertices de uma grade regular da capa, calcula uma matriz afim por triangulo e desenha a textura RGBA recortada no triangulo de destino. Isto **deforma a malha de fato**, nao move a imagem inteira. A cabeca gira discretamente em torno do pivo do pescoco e olhos abertos/fechados trocam opacidade nos quadros definidos. Nao adiciona Three.js, Live2D, Spine, Pixi, GPU ou dependencia npm nova.

- Codigo: `motion-remotion/src/mesh-rig.tsx` (SVG e funcoes puras de quadro).
- Validacao de assets: `videoforge/mesh_rig.py`.
- Integracao: `motion-remotion/src/scene-layer-preview.tsx`, `videoforge/remotion_preview.py`.
- Template **invalido ate ser preenchido e aprovado**: [RIG-CENA.template.json](modelos/RIG-CENA.template.json).
- Testes: `tests/test_mesh_rig.py`, `motion-remotion/tests/mesh-rig.test.cjs`.
- Workflow: `.github/workflows/remotion-animate-layers.yml`, entrada opcional `rig_run_id`.

## Preparar os cinco PNGs, sem duplicacoes

Todas as imagens devem ser **PNG RGBA8 nao interlacado** com o mesmo canvas integral da cena original (no teste atual, **1024 × 1536**), coordenadas, luz, escala e enquadramento. Nenhuma pode conter fundo opaco ou partes extras. Recomenda-se gerar por edicao da mesma cena-base com o Codex Proxy **somente com autorizacao de consumo**; os recortes exigem revisao humana e possivel correcao manual.

| Arquivo | Conteudo permitido | Conteudo proibido |
|---|---|---|
| `body-no-head-no-cape.png` | Torso, pernas, maos e itens de corpo, incluindo partes reconstruidas antes ocultas | Cabeca, olhos, capa |
| `head-no-eyes.png` | Cabeca/cabelo/pescoco com olhos removidos e area reconstruida | Torso duplicado, olhos abertos ou fechados |
| `eyes-open.png` | Somente os dois olhos abertos alinhados | Face, cabelo, pele fora da regiao dos olhos |
| `eyes-closed.png` | Somente os dois olhos fechados alinhados | Face, cabelo, olhos abertos |
| `cape.png` | Somente a capa vermelha isolada | Torso, rosto, telhado |

**Ordem de oclusao no MVP:** capa atras do corpo, depois corpo, depois cabeca/olhos, e por ultimo o primeiro plano do telhado. Se o desenho exigir partes da capa **na frente** do corpo, este MVP nao resolve sozinho: separar a capa em duas pecas ou evoluir o rig antes de aprovar.

O retangulo `cape_mesh.bounds` e o pivo `neck_pivot` estao em **pixels da imagem original**, nao na tela Shorts. O SVG preserva o aspect ratio 2:3 dentro do quadro 9:16, assim o pivo e os triangulos continuam alinhados ao `background` e `foreground`. Os valores do template sao **apenas exemplos**; medir a partir dos PNGs reais. Os triangulos devem cobrir toda a capa e apenas a capa, para nao cortar tecido nem deformar objetos vizinhos.

## Contrato de `rig.json`

O artifact do rig deve conter os cinco PNGs acima e `rig.json` na raiz. O schema e `videoforge/mesh-rig-assets/v1`; campos obrigatorios:

- `channel`, `video_id`, `scene` exatamente iguais ao artifact de origem.
- `source_sha256` igual ao hash SHA-256 da cena-base no manifesto verificado.
- `canvas.width`/`height` iguais a origem; `assets` mapeia os **cinco nomes fixos** para hashes SHA-256 dos PNGs.
- `neck_pivot.x/y` dentro da imagem; `head_max_deg` entre 0,05 e 2 graus.
- `blink_frames`: 1 a 10 quadros centrais, em ordem crescente, separados por pelo menos 12 quadros, dentro da duracao. Em cada centro os olhos fecham por 3 quadros, com transicao de 1 quadro em cada lado.
- `cape_mesh.bounds`: `x,y,width,height` em pixels, dentro do canvas; `columns` 2–6; `rows` 2–8; `amplitude_px` 0,1–12.
- `human_review.no_duplicate_parts`, `pixel_alignment` e `occlusion_order` devem ser **true apos revisao humana real**. Nao marcar automaticamente para destravar o workflow.

O validador rejeita hashes errados, PNGs corrompidos/sem alfa real, nomes ou canal trocados, canvas divergente, parametros fora do limite, ausencia de revisao e caminhos symlink nos arquivos. **Nao consegue provar** por algoritmos simples que nao ha bordas duplicadas, olho desalinhado, artefatos de inpainting ou capa atravessando o corpo. Essas checagens continuam humanas.

## Executar localmente com sprites reais

Com o artifact do Teste 2 em `./input` e os cinco PNGs + `rig.json` em `./rig-input`:

```bash
python -m videoforge.remotion_preview prepare \
  --input-dir ./input --rig-dir ./rig-input \
  --channel otaku-br --video-id teste-proxy-20261113 --scene cena-01 \
  --duration 8 --preset equilibrado

cd motion-remotion
npm ci
npx remotion render src/index.ts VideoForgeLayerScene \
  ../output/otaku-br/videos/teste-proxy-20261113/animacoes/cena-01/remotion-teste.mp4 \
  --props=../output/otaku-br/videos/teste-proxy-20261113/animacoes/cena-01/remotion-props.json \
  --codec=h264 --concurrency=2
cd ..
python -m videoforge.remotion_preview verify \
  --channel otaku-br --video-id teste-proxy-20261113 --scene cena-01
```

Requer FFmpeg/FFprobe, Node/Remotion e navegador compativel. Em Actions, esses pacotes **ja estao na imagem GHCR** e nao sao instalados a cada render. O exemplo local com `npm ci` e so para uma maquina que ainda nao tem dependencias. O prepare nao sobrescreve resultados existentes; limpar o ambiente de teste antes de repetir, sem apagar assets de origem.

## Executar no GitHub Actions

O workflow `remotion-animate-layers.yml` continua aceitando o artifact verificado do Teste 2 via `source_run_id`. Se `rig_run_id` ficar **vazio**, executa exatamente o modo antigo, com capa desabilitada. Quando um **workflow autorizado** produzir um artifact aprovado com nome:

```text
rig-<channel>-<video_id>-<scene>-<rig_run_id>
```

pode-se informar seu run ID em `rig_run_id`; o job baixa o artifact, valida todos os arquivos e ativa o rig. **Este PR nao cria um gerador nem um artifact aprovado de rig**: portanto o modo novo ainda nao e executavel com os assets antigos. Nao inventar IDs de runs nem marcar uma imagem como revisada sem a revisao.

## QA e criterios de aceitacao

1. `tsc --noEmit` e `node --test tests/mesh-rig.test.cjs`: testa transformacao afim, repetibilidade, costura superior fixa, angulo dentro do limite e piscadas nos quadros exatos.
2. `python -m unittest tests.test_mesh_rig tests.test_remotion_preview -v`: contrato de canal/cena, SHA, PNG RGBA, aprovacao de assets, compatibilidade com modo antigo e relatorio tecnico.
3. `verify`: confere MP4 H.264/AAC, duracao, resolucao e quadros distintos; marca `body_part_rigging_implemented=true` **somente** quando props de rig foram efetivamente preparados. `visual_review=pending` e `publishable=false` continuam.
4. **QA visual obrigatorio**: comparar quadros 0, 38–42, 60, 132 e 239 em 100% de zoom; verificar piscada, pivo no pescoco, silhueta da capa, juntas, z-index, costuras entre triangulos e ausencia de duplicacao. Comparar dois renders de quadros especificos para verificar estabilidade temporal. Mudancas de codec podem alterar bytes MP4 sem mudar geometria.
5. Se surgirem linhas entre triangulos (rasterizacao/antialias), limitar amplitude e densidade de grade, testar render no Chrome do GHCR e considerar migrar o warp para Canvas 2D ou WebGL com fallback; **nao alegar qualidade visual sem assistir**.

## Limites e proximos passos

- O MVP nao tem malha de rosto/cabelo, IK de bracos, lip-sync, simulacao fisica completa, nem geracao automatica de sprites; implementa **malha real da capa + pivo de cabeca + blink**.
- Os movimentos sao deterministas em `frame/fps`, sem `setInterval`, `Math.random` ou estado persistente. SVG evita exigir GPU no runner headless; o custo pode aumentar com numero de triangulos.
- Proximo passo operacional: gerar/reconstruir os cinco PNGs com o mesmo original, medir bounds/pivo, revisar manualmente, preencher os hashes e produzir um artifact de rig de um run autorizado. **So depois** executar a renderizacao real e revisar o MP4.
- Respeitar direitos sobre arte, modelos e trilha, especialmente personagens de franquias existentes. Nao publicar sem verificacao editorial e direitos.
- Para licenciamento do proprio Remotion em escala/comercial, consultar [Remotion licensing](https://www.remotion.dev/docs/license/pricing). Documentacao do mecanismo de renderizacao: [Remotion render](https://www.remotion.dev/docs/cli/render); [SVG transforms](https://developer.mozilla.org/en-US/docs/Web/SVG/Attribute/transform).

## Proxima etapa implementada: preparar candidata com 6 sprites e QA

Leia [preparação do rig candidato](PREPARAR-RIG-CANDIDATO.md). Para a arte real, o segundo olho aparece parcialmente sob a franja e a capa possui sobreposicao na frente do peito. O motor aceita um **sexto sprite opcional `cape-front.png`**: a parte traseira `cape.png` é desenhada atrás do corpo, a parte frontal após o corpo, ambas com o mesmo warp por malha, antes da cabeça. A extração manual por máscaras usando a cena verificada produz apenas **rascunho** com `human_review=false`, sem inpainting nem MP4 aprovado.
