# Regra principal de produção — VideoForge-IA

**Meta operacional:** um vídeo oficial PUBLICADO por canal por dia: cinco canais, cinco vídeos por dia. Isso é uma meta a alcançar, não publicação já obtida. Preview, job SUCCESS e MP4 técnico não contam.

## Duas filas independentes
- ESTEIRA DIÁRIA: pesquisa verificada do YouTube, checagem antirrepetição, roteiro, reutilização de personagens/cenários/rigs previamente aprovados, narração, legendas, montagem, MP4 validado, publicação com confirmação real da YouTube API e armazenamento de ID, horário, SHA e URL.
- LABORATÓRIO: rigs complexos, 40 tomadas cinematográficas, pixel-perfect, novas máscaras e correções de personagens. Erros dessa fila não devem bloquear outro conteúdo/canal que não dependa deles.

## Tratamento de exceções
Quando um episódio está bloqueado por qualidade, selecione outra pauta original do mesmo canal, se houver fonte e ativos aprovados. Não inventar pesquisas ou candidatos. Rejeições explícitas permanecem ativas. Não preencher pixels ocultos nem publicar material incorreto para bater metas. Reutilize pacotes de personagens aprovados, exija QA completo apenas na mudança de identidade/asset e faça testes curtos em lote nos outros vídeos. Marque BLOQUEADO quando não existir saída legítima.

## Estado real em 16/11/2026
O workflow .github/workflows/producao-oficial.yml possui bloqueio intencional por falta de executor oficial. O remake-autonomy.yml não é publicador diário. O novo daily-production-readiness.yml é só DIAGNÓSTICO read-only, não produz nem publica MP4. Os candidatos dos cinco canais estão inicialmente vazios e alguns históricos não têm YouTube API importada. É proibido contar essas tarefas como vídeos entregues.

**Prioridade técnica máxima:** integrar o executor de MP4 oficial e a publicação verificável, alimentação editorial com YouTube API, cache de ativos e fallback por canal. Reduzir o trabalho manual repetitivo de ROI do EP01 para exceções justificadas. Documentar diariamente publicados reais, pendências e causas.
