# Vídeos de Conde Games

Para cada vídeo realmente aprovado, usar:

```text
canal/gamer/videos/<video-id>/video.json
canal/gamer/videos/<video-id>/imagens/  (não versionar)
canal/gamer/videos/<video-id>/voz/      (não versionar)
output/gamer/videos/<video-id>/video.mp4
output/gamer/videos/<video-id>/video.qa.json
```

`video.json.modelo` opcional tem prioridade sobre `canal.json.modelo_padrao`.
No MVP, apenas `otaku-br` com modelo `imagem-estatica` está habilitado para composição, recebendo imagens e vozes externas já existentes. O modelo `camadas-animadas` ainda não realiza animação.
Nenhuma mídia é gerada ou publicada automaticamente.
