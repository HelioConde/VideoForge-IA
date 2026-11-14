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

## Quantidade de cenas e QA

O novo padrão **não fixa teto de cenas**. Roteiros do Otaku Multicena podem usar 1, 16, 25 ou mais cenas conforme a história, respeitando a duração de 90–180s deste piloto. O motor não pode rejeitar ou cortar cenas devido ao tamanho da lista. Continuam obrigatórios: validação de cada asset, orçamento de IA autorizado, ausência de duplicação/recorte de personagens, voz e legendas, verificação técnica de MP4 e revisão visual antes de publicar. O animático de Spy x Family é apenas uma prévia, não um vídeo final aprovado.

## Registro editorial adicional

Antes de reservar pauta ou gerar vídeo, siga `../../../docs/REGRAS-EDITORIAIS.md`. Crie `editorial.json` dentro da pasta do episódio usando `../../../docs/modelos/REGISTRO-EDITORIAL-VIDEO.template.json` como referência **editorial**, sem substituir o `video.json` técnico. Atualize `../editorial/historico-videos.json` ao cadastrar ou mudar o estado de um vídeo. Não alegar inexistência de assunto repetido com o histórico inicialmente vazio.
