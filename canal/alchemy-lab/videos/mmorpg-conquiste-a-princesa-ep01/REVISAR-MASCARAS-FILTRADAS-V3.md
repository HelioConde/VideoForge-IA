# EP01 — máscaras candidatas V3

![Comparação antes/depois, sem aprovação](QA-ROI-EXCLUSOES-V3.jpg)


## 16/11/2026 — Candidatas V3 e integridade de pixels (PR #63)

Corrigida a direção da exclusão no tecido externo de Aldric sentado, após inspeção do original: V2 atingia dobras acima da haste. V3 recupera 472 pixels e remove outros 258 em relação à V2; total excluído frente à máscara inicial: 487. Sete máscaras restantes idênticas por SHA. V2 e fontes originais preservadas. Não é aprovação semântica: EVIDENCIA_INSUFICIENTE nas oito regiões.

Programa valida RGB original, alfa somente subtrativo, recorte completo e contagem. Áreas protegidas bloqueiam exclusões sobre tecido anotado. 22 testes locais de ROI passaram; CI da branch será conferida antes do merge. Novo workflow qa-wardrobe-roi-pr.yml não gera imagens nem escreve no repositório. Produtor existente exporta V3 sem sobrescrever V2.

Arquivos: ROI-EXCLUSOES-CANDIDATAS-V3.json, QA-ROI-EXCLUSOES-V3.json, QA-ROI-EXCLUSOES-V3.jpg e assets/qa-roi-exclusions-v3/. Revisão: REVISAR-MASCARAS-FILTRADAS-V3.md. R2, MP4 e YouTube continuam bloqueados, zero chamadas pagas. Próximo passo: validar CI e integração; revisar barba/boca/gola, bordados e corpete pequeno contra as fontes completas antes de alterar contrato semântico.

[Versão anterior preservada](REVISAR-MASCARAS-FILTRADAS-V2.md) | [Relatório V3](QA-ROI-EXCLUSOES-V3.json)

## 16/11/2026 — V3 integrada e executada no GitHub

PR [#63](https://github.com/HelioConde/VideoForge-IA/pull/63) integrado: [f5a7f3e](https://github.com/HelioConde/VideoForge-IA/commit/f5a7f3e779c0f9284a5f3947f51bfd74084963e5). QA do PR [43942403827](https://github.com/HelioConde/VideoForge-IA/actions/runs/43942403827): SUCCESS, 22 testes ROI. Produtor main [43942596191](https://github.com/HelioConde/VideoForge-IA/actions/runs/43942596191): SUCCESS, 8 testes de exclusões e exportação V3. Commit de saída: f3ce91e. Depois do fetch, SHA das oito fontes e oito máscaras conferidos. PNGs V2 preservados; JPEG V3 foi reexportado pelo Pillow do runner.

A candidata de tecido externo Aldric A recupera 472 pixels e remove outros 258 versus V2; sete máscaras restantes idênticas por SHA. Nenhuma máscara semanticamente aprovada: 0/8, 0/4 pares oficiais; R2/MP4/YouTube bloqueados, zero chamadas pagas. Próximo passo: inspecionar os originais completos e as bordas V3 para barba/boca/gola, adornos e corpete B; não promover contrato por testes de integridade.

## 16/11/2026 — Revisão contextual das oito máscaras V3

Programa agora exporta QA-ROI-CONTEXTO-V3.jpg com quatro colunas alinhadas: fonte com contexto, máscara anterior, pixels removidos e máscara final. O contexto é recortado da fonte SHA e amplia apenas a prévia; coordenadas e SHA da prancha constam no relatório V3. Medições continuam em pixels nativos, nunca no JPEG. Oito PNGs finais mantêm exatamente os hashes anteriores.

Inspeção: corpete B representa cobertura parcial e oclusões de manga/cabelo/adornos. Não expandir por cor nem preencher partes ocultas automaticamente. Barba B ainda exige separação boca/bigode. 25 testes ROI locais passaram, incluindo alinhamento, pixels removidos exatos e bordas sem padding. CI e publicação desta mudança ainda pendentes nesta entrada. Zero máscaras aprovadas e R2 bloqueada; próxima etapa é revisão semântica no contexto original.
