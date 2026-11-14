# Animação de camadas separadas — legado FFmpeg (fallback de teste)

Versão inicial: 13/11/2026. Este teste usa **as imagens que o VideoForge-IA já criou e separou**, sem gerar imagens novas e sem gastar chamadas de IA. Executa FFmpeg da imagem Docker precompilada no GHCR, sem instalar Go ou FFmpeg por job.

## Padrão obrigatório para o pipeline novo — cena-mãe → camadas RGBA → rig → montagem

**Para QUALQUER vídeo animado, não basta deslocar a ilustração inteira.** Cada cena deve cumprir:

1. **Cena-mãe original:** gerar e guardar a imagem completa no programa, com SHA-256, ID de canal/vídeo/cena, dimensões, enquadramento, pose, figurino, perspectiva, luz e estilo. É a única referência visual para derivar os recortes dessa cena.
2. **Background reconstruído:** editar A PRÓPRIA cena-mãe para retirar personagens e objetos móveis, preenchendo a parte originalmente escondida. Preservar tamanho, perspectiva, iluminação e coordenadas; não inventar um cenário novo.
3. **Personagens separados:** editar A MESMA cena-mãe para extrair cada personagem/parte que se moverá em PNG **RGBA com transparência alfa real** e na mesma posição/escala. Extrair objetos móveis e foreground separadamente se existirem na cena; não inventar objetos ausentes.
4. **Sem duplicação:** a camada base não pode manter o cabelo/capa/braço/objeto que será desenhado novamente como sprite animável. Restaurar partes encobertas de corpo/cenário antes do movimento. Sobrepor tecido na costura, manter pivôs corretos e rosto-base opaco durante piscadas.
5. **Animação verdadeira:** Remotion/rig movimenta personagem, olhos/cabelo/roupas/objetos isolados, com movimentos sutis naturais e vento quando cabível. Movimento de câmera ou pan **é adicional**, não substituto do rig.
6. **QA fail-closed:** verificar SHA da cena-mãe em todas as camadas, PNG RGBA/transparência real, dimensões, alinhamento, ausência de recortes/duplicações, movimento de partes independentes, olhos, rosto, bordas e costuras em vários quadros, narração e legendas. Se algum componente essencial faltar: `pipeline_pendente`; `rig_animado_aplicado=false`; `video_oficial_do_programa=false`. Nunca declarar vídeo oficial com MP4 de pan.
7. **Sem teto de cenas:** a quantidade vem do roteiro; limites de orçamento de inferência, tempo de execução, licenças e duração são controles **separados**. Não consumir chamadas adicionais sem orçamento autorizado.
8. **Local de execução:** usar exclusivamente os módulos reutilizáveis do `HelioConde/VideoForge-IA` e GitHub Actions. Guardar assets e QA por canal/cena, publicar artifacts de revisão, nunca publicar no YouTube sem aprovação.

Ver `docs/PADRAO-ANIMACAO-POR-CAMADAS.md` e `docs/TESTE-CAMADAS-CENA.md`. O exemplo da capa vermelha foi um experimento de rig para outra cena: jamais reutilizar automaticamente seus prompts de aventureiro, cabelo castanho, espada ou capa em outros personagens.

## O que está implementado

- **Background**: deslocamento lento de câmera com overscan para evitar bordas vazias (parallax).
- **Personagem principal**: oscilação vertical e horizontal suave, como respiração e leve flutuação.
- **Foreground/telhado**: deslocamento próprio e mais próximo da câmera para dar profundidade.
- **Entrada verificada**: artifact real do Teste 2, com cena-base, background, character-main, foreground-roof e manifesto; os arquivos são checados por SHA-256, dimensões e transparência ANTES de renderizar.
- **Saída real**: MP4 vertical 1080×1920, 24 fps, H.264 e AAC, com **trilha silenciosa** somente para teste técnico. Duração permitida de 4–12 s; opções manuais 6, 8 ou 10 s.
- **QA**: codecs, duração, proporção, SHA-256, verificação de que dois quadros decodificados em instantes diferentes possuem hashes diferentes. O status técnico não é aprovação visual nem comprovação de animação de articulações.

A cena renderizada usa **três camadas**. O arquivo separado da capa existe, mas **não é sobreposto ainda**, pois a capa original continua visível na imagem do personagem. Sobrepô-la geraria duplicação. Para animá-la independentemente é necessário produzir um personagem sem capa ou uma máscara/rig revisada visualmente. Também não há movimentação individual de braços, rosto, olhos, cabelo ou espada nesta fase.

## Workflow manual

[VideoForge — Teste 3 animar camadas separadas (MP4)](../.github/workflows/animate-separated-layers.yml)

No GitHub Actions, selecione Run workflow, branch `main`, e utilize:

- `source_run_id=43437992955` (run real aprovado do Teste 2)
- `channel=otaku-br`
- `video_id=teste-proxy-20261113`
- `scene=cena-01`
- `duration=8`
- `preset=cinematic`

O programa baixa o artifact `camadas-advanced-otaku-br-teste-proxy-20261113-cena-01-43437992955`, executa `python -m videoforge.animate_layers` e envia apenas o MP4 de prévia, manifesto de movimentos e QA como artifact do próprio job. Não lê accounts.json nem conecta ao Codex Proxy nesta etapa.

Artefacts do GitHub têm expiração (7 dias nos testes de camadas e prévias). Se os arquivos tiverem expirado, repetir a separação usando a imagem original, caso ainda exista, ou gerar uma nova cena quando houver autorização para gastar uma nova inferência.

## Arquivos gerados

```text
output/otaku-br/videos/teste-proxy-20261113/
  assets/cena-01/                # importados e verificados do artifact anterior
    cena-base.png
    background.png
    character-main.png
    foreground-roof.png
    cape.png
    manifest.json
  animacoes/cena-01/
    teste-parallax.mp4
    teste-parallax.qa.json
    movimentos.json
```

Esses arquivos ficam no artifact do GitHub e em `output/` ignorado pelo Git; **não há upload ao YouTube** nem alteração do formato `canal/<id>/videos/<video-id>/video.json`.

## Regras e limites

1. Sem regeneração de imagem no workflow de animação. Toda cena é recuperada do run anterior, verificada por hash e separada por canal.
2. As camadas são de edição generativa, não segmentação pixel-perfect. O parallax pode revelar imperfeições de recorte, inpainting ou alinhamento.
3. Não reutilizar `cape.png` ou `hair.png` como overlay sobre o personagem completo sem remover a versão original desses elementos do sprite-base. Não fingir que animação de corpo inteiro é animação de articulações.
4. Vídeo de prévia não tem roteiro, narração, sincronização labial, música nem Shorts final. O AAC é silêncio gerado localmente.
5. `modelos/camadas-animadas/modelo.json` continua `operacional=false` para a produção completa; apenas o teste independente de parallax está disponível.
6. Ao aprovar o teste, o próximo módulo deve criar máscaras do personagem sem capa e definir pivôs, segmentos de braços/cabeça, quadros-chave, interpolação e verificação visual antes de habilitar o modelo animado real.
7. Os testes offline rodam em PR/push e não acionam IA, produção ou YouTube.

Comando local quando o artifact estiver extraído:

```bash
python -m videoforge.animate_layers --input-dir ./input --channel otaku-br --video-id teste-proxy-20261113 --scene cena-01 --duration 8 --preset cinematic
```

## Substituição pelo Remotion do projeto antigo

O fluxo preferido para refazer as animações agora está no [guia Remotion](REMOTION-ANIMACAO.md) e no workflow `remotion-animate-layers.yml`. O motor FFmpeg desta página continua disponível apenas como comparação/regressão; a animação por quadro no teste novo é renderizada pelo Remotion antigo.
