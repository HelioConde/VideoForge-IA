# QA temporal de animação articulada

Consultar para avaliar movimento ou investigar defeitos que aparecem em determinados frames. Complementa a integridade estática, não aprova estética automaticamente.

Receba tomada, commit, fonte/manifesto, FPS, duração e critérios da ação. Identifique se a evidência vem de fixture, peças reais ou render; não misture os níveis.

## O que verificar

- Torso cortado: localizar primeiro frame ruim; comparar alpha/crop, offset/pivô, camada oclusora e limite da câmera.
- Contato escorregando: medir pontos no mesmo espaço em todos os frames do intervalo de contato; observar também o vídeo.
- Junta aberta: verificar continuidade e underlay na pose neutra e extremos; localizar a parte que revelou o fundo.
- Deformação: procurar triângulos invertidos/colapsados, raízes móveis quando deveriam estar presas e perda de silhueta.
- Temporal: procurar saltos de pose, troca brusca de ordem visual, frames congelados e emendas de loop, quando houver loop.

Teste invariantes baratos em todos os frames de uma tomada curta. Amostras de início, antecipação, contato, extremos e final ajudam a diagnosticar, mas não descartam um defeito de um único quadro. Assista à prévia completa para avaliar ritmo e naturalidade; se não houver vídeo, declare essa limitação.

## Reprodução

Compare poses do mesmo frame por acesso direto, sequência crescente e fora de ordem, repetindo um frame. Para comparar pixels, fixe ambiente, assets e carregamento. Compare frames decodificados; diferenças no hash do contêiner MP4 podem vir de metadados/codificação. Um teste de pose não comprova igualdade dos pixels renderizados.

## Resultado acionável

Cada falha informa frame/intervalo, parte, coordenada quando pertinente, critério, evidência e comando reproduzível. Separe falha técnica, suspeita visual, ausência de evidência e aprovação humana registrada. Devolva a correção ao responsável; não altere gates ou tolerâncias para aprovar o resultado.

Após uma correção, repita os checks afetados e verifique ausência de regressão na mesma ação. Evite gerar relatórios sucessivos sem uma decisão nova. Se o defeito persistir sem progresso, classifique se a causa é arte, geometria, timing ou render antes de repetir.

Procedimento próprio do VideoForge, 17/11/2026. Render e publicação continuam sujeitos aos workflows e bloqueios vigentes.
