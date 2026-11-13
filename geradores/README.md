# Geradores especializados — contrato reservado

Mesmo conceito do VideoForge anterior: `geradores/<id>/gerador.json` descreve a **receita editorial** (anime, kids, gamer etc.). `modelos/<id>/modelo.json` descreve o **processo técnico** (estático, camadas etc.).

Nesta versão, geradores especializados **ainda não estão implementados nem autorizados a gastar IA**. Os campos `gerador_padrao` em `canal.json` são metadados planejados; não são provas de execução. Quando necessários, deverão ser implementados em novas pastas isoladas, com testes e orçamento explícito.
