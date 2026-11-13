# Vídeos de Emanuelly Kids

Para cada vídeo realmente aprovado, usar:

```text
canal/manu-kids/videos/<video-id>/video.json
canal/manu-kids/videos/<video-id>/imagens/  (não versionar)
canal/manu-kids/videos/<video-id>/voz/      (não versionar)
output/manu-kids/videos/<video-id>/video.mp4
output/manu-kids/videos/<video-id>/video.qa.json
```

`video.json.modelo` opcional tem prioridade sobre `canal.json.modelo_padrao`.
No MVP, apenas `otaku-br` com modelo `imagem-estatica` está habilitado para composição, recebendo imagens e vozes externas já existentes. O modelo `camadas-animadas` ainda não realiza animação.
Nenhuma mídia é gerada ou publicada automaticamente.
