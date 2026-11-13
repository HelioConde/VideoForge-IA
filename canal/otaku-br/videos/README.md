# Vídeos de Otaku Multicena

Para cada vídeo realmente aprovado, usar:

```text
canal/otaku-br/videos/<video-id>/video.json
canal/otaku-br/videos/<video-id>/imagens/  (não versionar)
canal/otaku-br/videos/<video-id>/voz/      (não versionar)
output/otaku-br/videos/<video-id>/video.mp4
output/otaku-br/videos/<video-id>/video.qa.json
```

`video.json.modelo` opcional tem prioridade sobre `canal.json.modelo_padrao`.
No MVP, apenas `otaku-br` com modelo `imagem-estatica` está habilitado para composição, recebendo imagens e vozes externas já existentes. O modelo `camadas-animadas` ainda não realiza animação.
Nenhuma mídia é gerada ou publicada automaticamente.

## Registro editorial adicional

Antes de reservar pauta ou gerar vídeo, siga `../../../docs/REGRAS-EDITORIAIS.md`. Crie `editorial.json` dentro da pasta do episódio usando `../../../docs/modelos/REGISTRO-EDITORIAL-VIDEO.template.json` como referência **editorial**, sem substituir o `video.json` técnico. Atualize `../editorial/historico-videos.json` ao cadastrar ou mudar o estado de um vídeo. Não alegar inexistência de assunto repetido com o histórico inicialmente vazio.
