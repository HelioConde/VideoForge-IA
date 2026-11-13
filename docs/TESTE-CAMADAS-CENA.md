# Testar uma cena separada em camadas — VideoForge IA

Registro tecnico em 13/11/2026. O objetivo e **editar a MESMA imagem ja gerada no programa**, usando a rota de edicao do Codex Proxy, para recuperar fundo, personagem, objetos a frente e pecas possivelmente animaveis.

## Cena original confirmada

A primeira imagem real do Otaku Multicena esta no [workflow de origem](https://github.com/HelioConde/VideoForge-IA/actions/runs/43433023378). O artefato se chama `imagem-otaku-br-teste-proxy-20261113-43433023378`. Possui `cena-01.png` e `cena-01.meta.json`. O artifact original expira conforme retencao de 3 dias; quando expirar, gerar nova cena por `proxy-images.yml` e informar o respectivo run ID.

Os workflows de separacao NAO geram uma segunda cena principal. O `actions/download-artifact@v4` baixa a cena original ou o artifact do teste anterior. O cliente envia sempre a `cena-base.png` pelo campo `images[0].image_url` de `POST /v1/images/edits`.

## Etapa 1 — separar background e personagem

Abra [Teste 1 no Actions](../.github/workflows/scene-layers-basic.yml) e selecione Run workflow, branch `main`. Por padrao, use:

- source_run_id: `43433023378`
- channel: `otaku-br`
- video_id: `teste-proxy-20261113`
- scene: `cena-01`
- mode: `ephemeral`
- model: `gpt-image-2`

O teste faz no maximo DUAS edicoes sequenciais: `background.png` sem o personagem, depois `character-main.png` com transparencia alfa verdadeira. A geracao pode falhar se o modelo nao retornar PNG com canal alfa; nesse caso o CI deve ficar vermelho, mesmo se a API tiver respondido. O artifact e `camadas-basic-otaku-br-teste-proxy-20261113-cena-01-<run_id>`.

## Etapa 2 — primeiro plano e objetos para animacao

Apos o Teste 1 passar, abra [Teste 2 no Actions](../.github/workflows/scene-layers-advanced.yml). Informe `source_run_id` igual ao **numero do run do Teste 1**, e mantenha canal/video/cena identicos. O Teste 2 baixa e verifica os arquivos da etapa anterior por hash.

- `component=pair` (padrao) gera `foreground-roof.png` e `cape.png` (no maximo 2 chamadas).
- `component=hair`, `sword`, `flag` ou `waterfall` permite testar individualmente as pecas presentes na cena, um chamado por run.
- Se a cena nao mostrar o objeto, NAO tentar inventa-lo.
- Cada run avancado parte do artifact da etapa basica; nao combina automaticamente varios artifacts avancados. Agregacao e montagem ficam para proxima etapa.

Usar a imagem como referencia **nao garante segmentacao pixel-perfeita**. O modelo pode alterar detalhes de rosto, anatomia, proporcoes, fundo, capa e coordenadas. O Teste 2 NAO e rig nem animacao: apenas recupera candidatos a camadas e um manifesto para revisao.

## Organizacao dos artifacts por canal

```text
output/<canal>/videos/<video-id>/assets/<cena>/
  cena-base.png
  background.png
  character-main.png
  foreground-roof.png  # opcional do Teste 2
  cape.png             # opcional do Teste 2
  hair.png             # opcional, em run separado
  sword.png            # opcional, em run separado
  flag.png             # opcional, em run separado
  waterfall.png        # opcional, em run separado
  manifest.json
```

O manifesto armazena hashes SHA-256, dimensoes, camada, ordem de profundidade sugerida, verificacao de PNG/transparencia, modelo e aprovacoes pendentes. Ele NAO altera `video.json` ou o renderizador MP4 existente.

## QA e custos

1. Antes de gastar cota: validar IDs, Secrets e se o artifact original existe.
2. Fundo: PNG com as mesmas dimensoes da origem e pixels opacos; a ausencia visual de personagem ainda requer revisao humana.
3. Personagem, primeiro plano e itens: PNG RGBA8, verificacao efetiva de pixels transparentes e pixels visiveis. Recusa PNG RGB opaco ou textura quadriculada que finge transparencia.
4. O alinhamento pixel a pixel, inpainting, continuidade visual, ausencia de elementos duplicados e movimentacao futura exigem revisao separada: nenhum teste tecnico comprova isso.
5. Falha nao recebe status de aprovado. Artifact parcial e enviado para diagnostico; nao geramos MP4 nem fazemos upload no YouTube.
6. O motor compartilha a imagem Docker precompilada do Codex Proxy. Nao instala Go, nao roda durante push/PR, nao faz retries cegos contra HTTP 429.
7. Cada run de teste usa no maximo 2 chamadas de edicao, mas chamadas falhas tambem podem consumir cota. Nao executar testes repetidamente sem analisar os resultados.
8. O modo ephemeral nao salva refresh tokens atualizados: e temporario. Para operacao continua e necessario proxy persistente com HTTPS e armazenamento protegido.

O codigo fica em `videoforge/scene_layers.py` e os testes em `tests/test_scene_layers.py`. Testes offline com PNGs sinteticos e API simulada:

```bash
python -m unittest discover -s tests -v
```

Os workflows sao apenas de validacao das etapas de arte. O `modelos/camadas-animadas` ainda nao e renderizador operacional.
