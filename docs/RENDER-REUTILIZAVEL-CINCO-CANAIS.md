# Render reutilizável para os cinco canais — issue #66

**Workflow:** `.github/workflows/render-real-multichannel.yml`. Executar manualmente selecionando `channel` e `video_id`. Não usa proxy, não gera imagens/áudio e não publica YouTube.

A pasta `canal/<channel>/videos/<video-id>/` precisa conter `video.json` (`videoforge/mvp/v1`) mais todas as imagens e narrações reais referenciadas em `scenes`. O validador recusa manifestos sem mídia, paths fora do canal, formatos diferentes e vídeos sem áudio.

O compositor existente `videoforge.mvp` gera H.264 1080×1920 com AAC, verifica duração, SHA, FFprobe e cria `video.qa.json`. Saída como artifact temporário; **é um MP4 técnico de mídia real**, não prova de aprovação artística, direitos ou upload. Não reutilizar cenas de outros canais sem revisão de direitos e identidade.

**Ainda falta para um vídeo diário:** ingestão automática de assets provenientes dos geradores com SHA/proveniência; política de aprovação visual reutilizável; seleção editorial verificada; upload/checagem via YouTube API; fluxo de fallback. O workflow `producao-oficial.yml` continua bloqueado intencionalmente até integrar esses passos. Não alterar suas barreiras apenas para obter SUCCESS.

O render não impõe um limite arbitrário de cenas; o MVP atual exige vídeos de 90 a 180 segundos. O caminho cinematográfico 40 tomadas/Three.js é separado.
