# Vídeos de Otaku Reframe

Para cada vídeo realmente aprovado, usar:

```text
canal/otaku-en/videos/<video-id>/video.json
canal/otaku-en/videos/<video-id>/imagens/  (não versionar)
canal/otaku-en/videos/<video-id>/voz/      (não versionar)
output/otaku-en/videos/<video-id>/video.mp4
output/otaku-en/videos/<video-id>/video.qa.json
```

`video.json.modelo` opcional tem prioridade sobre `canal.json.modelo_padrao`.
No MVP, apenas `otaku-br` com modelo `imagem-estatica` está habilitado para composição, recebendo imagens e vozes externas já existentes. O modelo `camadas-animadas` ainda não realiza animação.
Nenhuma mídia é gerada ou publicada automaticamente.
