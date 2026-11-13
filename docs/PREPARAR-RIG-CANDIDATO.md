# Preparação de sprites candidatos de personagem — Otaku Multicena

**Estado: prévia técnica / não aprovado.** Este estágio aplica a [pesquisa de rig 2D](RIG-MALHA-2D.md) sem inventar aprovação, sem chamadas de IA e sem vídeo publicável. O motor Remotion já foi integrado na PR #33; este trabalho prepara **sprites candidatos** para futura inspeção e reconstrução.

## Evidência e particularidades reais da cena

- Cena: `canal/otaku-br/videos/teste-proxy-20261113/cena-01`.
- Origem técnica: [run 43437992955](https://github.com/HelioConde/VideoForge-IA/actions/runs/43437992955), artifact `camadas-advanced-otaku-br-teste-proxy-20261113-cena-01-43437992955`.
- Imagens de entrada com hashes conferidos: `cena-base.png`, `character-main.png`, `cape.png`, `background.png`, `foreground-roof.png` e `manifest.json` (1024×1536).
- Inspeção ampliada: personagem de cabelo castanho com **olho principal + segundo olho parcialmente visível sob franja**; capa vermelha atravessa frente do ombro/peito e também passa atrás do corpo. Não animar a capa como overlay único.
- A fonte não contém corpo completo **atrás** da capa. É incorreto afirmar que uma segmentação produz automaticamente costas e pescoço perfeitos.

## Implementado — sem downloads de modelos

O programa [`videoforge/rig_candidate.py`](../videoforge/rig_candidate.py) recebe o artifact original e um [plano de máscaras por canal](../canal/otaku-br/videos/teste-proxy-20261113/rig-plan.json) com pontos de polígonos **provisórios**. Ele:

1. Verifica canal/vídeo/cena, hashes, manifesto, dimensões e RGBA da origem, falhando se houver divergência.
2. Rasteriza máscaras de cabeça, **duas áreas de olhos** e região da capa que deve passar à frente.
3. Preserva os pixels da imagem original nos recortes; não solicita uma nova cena/novo personagem.
4. Gera cinco sprites tradicionais e o sexto `cape-front.png`, separando capa traseira/frontal. O Remotion suporta o sexto sprite opcionalmente, com a **mesma deformação de malha** e ordem de desenho apropriada.
5. Desenha pálpebras fechadas provisórias e preenche região dos olhos com amostra simples de pele (sem considerar isso inpainting final).
6. **Remove**, mas **não reconstrói**, áreas ocultas do corpo. Essas lacunas são registradas como risco mensurável.
7. Produz `contact-sheet.png` com quatro quadros (original, recomposição em posição neutra, mapa de diferenças, máscaras e pivô), `asset-provenance.json` e `candidate.qa.json`.
8. Escreve `rig.json` com os hashes e `human_review=false` para todos os requisitos; a validação do render final **obrigatoriamente rejeita o candidato**.

Não há geração paga, OpenCV/SAM2/LaMa obrigatório, modelos externos nem novas dependências. Os PNGs são decodificados com FFmpeg já instalado e gravados pela biblioteca padrão Python. O artefato mantém o nome **`rig-candidate-...`**, nunca o nome `rig-...` exigido pelo renderizador de produção.

## Executar no GitHub ou local

Workflow: [Preparar rig candidato RGBA sem IA](../.github/workflows/rig-candidate.yml). Ele recupera o artifact existente, usa a imagem GHCR Remotion pré-compilada e publica o ZIP com prévias e sprites. O processamento real é executado por `workflow_dispatch` e uma vez no `push` de alterações relevantes à `main`; não roda a cada commit de PR.

Execução local (Python 3.12+ e FFmpeg já disponíveis):

```bash
python -m videoforge.rig_candidate \
  --source-dir ./source-layers \
  --plan ./canal/otaku-br/videos/teste-proxy-20261113/rig-plan.json \
  --output-dir ./output/otaku-br/videos/teste-proxy-20261113/rig-candidates/cena-01
```

O destino precisa estar vazio. Não colocar PNGs, vídeos ou credenciais no Git. Os dados da cena ficam **somente** no artifact e em `output/otaku-br/videos/teste-proxy-20261113/`.

## O que falta para o primeiro vídeo com o rig real

**Etapa 1 — revisar máscaras candidatas.** Comparar o contato e cada PNG em 100% de zoom: franjas, olhos, linha do pescoço, broche/capa, manga, costuras, posição do segundo olho e oclusões. Corrigir os polígonos; não inferir automaticamente que cada recorte é perfeito.

**Etapa 2 — reconstruir somente partes ausentes.** Com ferramenta local ou edição humana, preencher pescoço/ombros/costas sob capa e cabeça, sem redesenhar áreas visíveis. Pequenas regiões podem receber [OpenCV inpaint](https://docs.opencv.org/4.x/df/d3d/tutorial_py_inpainting.html); máscaras maiores podem exigir [LaMa](https://github.com/advimman/lama). Para refinamento de bordas e segmentação por prompt são opções de **etapa separada** [BiRefNet](https://github.com/ZhengPeng7/BiRefNet) e [SAM 2](https://github.com/facebookresearch/sam2). Não instalar esses modelos no runner de render a cada vídeo; avaliar licenças de todos os checkpoints.

**Etapa 3 — refinar olhos e oclusão.** Trocar o fechamento provisório por desenhos alinhados aos dois olhos, revisar as cores da pele e assegurar que `cape-front.png` não cubra mão, braço ou cabelo indevidamente.

**Etapa 4 — aprovar só depois de comparar.** Produzir máscara/heatmap de reconstrução, comparar pixels próximos de juntas, testar frames extremos `0, 38–42, 60, 132, 239` e inspeção na composição final com o telhado. O relatório automático não deve mudar `human_review` para verdadeiro. O operador deve revisar e assinar o conjunto por hash antes da promoção.

**Etapa 5 — gerar render real.** Somente após completar as lacunas e aprovar as seis peças, criar artifact com nome contratual `rig-<channel>-<video_id>-<scene>-<run_id>`, ativar `rig_run_id` no [workflow Remotion](../.github/workflows/remotion-animate-layers.yml), renderizar MP4 e fazer nova inspeção visual.

Critério: **motor técnico ≠ sprites visualmente corretos ≠ vídeo publicável**. A composição cinemática existente continua intacta quando `rig_run_id` está vazio.

## Métricas e direitos

- `pixel_rmse_visible` da contact sheet mede pixels na área de personagem sobre cinza; a RMSE pode ser alta por oclusão/alinhamento e não prova que o rig está ruim ou bom sozinho.
- `body_pixels_erased_without_inpainting` representa anatomia que precisará reconstrução, nunca é contabilizada como resolvida.
- `human_visual_approval=false`, `rig_ready_for_remotion=false` e `youtube_uploaded=false` por padrão.
- `asset-provenance.json` registra SHA-256 das entradas e plano. Isso não substitui verificação de direitos da arte ou licenças do Remotion e dos modelos.

## Prévia MOVIMENTADA de rascunho (apenas diagnóstico)

Existe um [workflow manual de render de rig em rascunho](../.github/workflows/rig-draft-preview.yml). Ele lê um artifact `rig-candidate-...` com seis sprites não aprovados e verifica hashes/estado `human_review=false`, junto ao artifact original da mesma cena. Gera cinco PNGs estáticos de quadros 0, 40, 60, 132 e 239, além de um MP4 técnico de **8 segundos com marca d'água permanente** `RASCUNHO — SEM RECONSTRUCAO/QA VISUAL`.

O processo usa a mesma malha SVG/head/blink do Remotion, mas o arquivo `videoforge/rig_draft_preview.py` cria props **isoladas, somente para revisão**, sem alterar o bloqueio de produção de `videoforge/mesh_rig.py`. A revisão de assets continua falsa; o QA do draft deve conter `publishable=false`, `youtube_uploaded=false` e `body_inpainting_completed=false`. Não comparar frames de câmera para declarar qualidade anatômica: observar juntas, olhos e capa em resolução integral.

O run de origem e o run do candidato são inputs explícitos; os artifacts expiram após prazo configurado. Um preview não habilita o canal, o modelo `camadas-animadas` ou publicação no YouTube.

## Refinamento natural da piscada — sem trocar o personagem

A etapa de olhos fechados foi aprimorada após observar o defeito visual do teste anterior: havia uma **faixa de pele plana** e **linhas escuras pixelizadas**, principalmente no olho de frente. O módulo [`videoforge/eye_refine.py`](../videoforge/eye_refine.py) corrige o recorte em coordenadas originais da cena:

- **Preenchimento local:** lê a textura RGB da bochecha original próxima aos olhos, com amostragem bilinear e borda suavizada. Não cola uma imagem de rosto diferente nem mistura estilos.
- **Pálpebra natural:** pinta linhas finas de Bézier com espessura variável, terminação afilada, tons marrons e sombra sutil antisserrilhada.
- **Dois olhos visíveis:** o segundo, parcialmente escondido sob a franja, recebe uma linha proporcionalmente menor.
- **Controle de arte:** o arquivo `rig-plan.json` deste vídeo define máscara, origem das amostras de pele e quatro pontos por curva para eventual correção precisa; esses dados não são uma solução para todas as cenas.
- **Proveniência:** nenhuma inferência de IA é necessária nessa fase. O retrato de olho fechado gerado como referência serve para orientar o **estilo**, mas não é aplicado diretamente ao sprite: enquadramento, escala e textura diferem da cena-base.
- **Bloqueio:** os sprites continuam como **candidatos**, `human_visual_approval=false` e `rig_ready_for_remotion=false`. A geração do MP4 continua com marca d'água e não publica no YouTube.

O workflow [`rig-eye-preview.yml`](../.github/workflows/rig-eye-preview.yml) recria as camadas a partir do artefato original (run 43437992955), testa a geometria e renderiza quadros **0, 38, 39, 40, 41, 42, 60 e 132** e o MP4 para inspeção humana, sem chamadas pagas. O mesmo módulo de olhos pode ser aproveitado em outros canais, desde que cada personagem possua máscara/curva/amostra de pele próprias. O código não cria camadas aprovadas automaticamente.
