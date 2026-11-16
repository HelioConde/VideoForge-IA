# Resultado do filtro de figurino — EP01 V2 (40 tomadas)

## Veredito resumido

**ALDRIC: REPROVADO — 2 problemas críticos reportados pelo proprietário.**
**ELARA (palácio): REPROVADA — 1 problema crítico reportado pelo proprietário.**
**KAEL: REVISÃO PENDENTE — não há defeito específico confirmado; isso não é aprovação.**
**ELARA (rua): REVISÃO PENDENTE — o corpete roxo NÃO é exigido no disfarce.**

Os problemas abaixo são baseados no seu relato e nas descrições semânticas, **não numa medição automática de pixels**. O sistema verificou a contradição entre as versões descritas; não inventou cores numéricas nem inspeções de fotos que não ocorreram.

## Diferenças filtradas

### ALDRIC — aldric_red_black_inversion (CRÍTICO, REPROVADO)

**Diferença:** Rei sentado: roupa externa VERMELHA e centro PRETO. Em pé: roupa externa PRETA e centro VERMELHO. As cores inverteram sem mudança de roupa.

**Correção exigida:** Fixar um único mapa de cores por área de tecido, mesma variante sentada ou em pé.

**Fonte da evidência:** relato visual explícito do proprietário; sem máscaras de roupa/barba nem coordenadas verificadas.

### ALDRIC — aldric_beard_color_changed (CRÍTICO, REPROVADO)

**Diferença:** Cor da barba muda e a identidade visual deixa de parecer o mesmo rei; tonalidades numéricas não medidas.

**Correção exigida:** Rever barba/cabelo contra uma referência individual aprovada; bloquear mudança de cor/silhueta sem arco narrativo.

**Fonte da evidência:** relato visual explícito do proprietário; sem máscaras de roupa/barba nem coordenadas verificadas.

### ELARA — elara_purple_bodice_missing (CRÍTICO, REPROVADO)

**Diferença:** Parte ROXA no peitoral do vestido real aparece em uma imagem e some ou muda na outra.

**Correção exigida:** Manter painel roxo exatamente no mesmo lugar, tamanho e traço do traje palaciano em todos os ângulos.

**Fonte da evidência:** relato visual explícito do proprietário; sem máscaras de roupa/barba nem coordenadas verificadas.

## Tomadas afetadas pelo risco da referência

**Aldric (7 tomadas):** C01-P03, C01-P04, C02-P01, C12-P02, C13-P01, C14-P01, C14-P02.

**Elara com traje real (6 tomadas):** C12-P02, C12-P03, C12-P04, C13-P01, C14-P01, C14-P02.

**Elara em disfarce (9 tomadas):** não foi aplicado o erro do peitoral roxo a esta variante narrativa.

Essas são **dependências bloqueadas**, não uma alegação de que cada PNG de cada tomada tenha sido inspecionado e reprovado.

## Checklists completos e provas visuais

- [Checklist de Aldric](CHECKLIST-FIGURINO-ALDRIC.json) — barba, cor exterior/central, gola, bordados, manto, coroa e pose
- [Checklist de Elara](CHECKLIST-FIGURINO-ELARA.json) — roxo do corpete, vestido e variante rua/palácio
- [Checklist de Kael](CHECKLIST-FIGURINO-KAEL.json) — capa vinho, ombreira dourada, pedra azul e variantes
- [Comparações de figurinos já arquivadas](REVISAR-DETALHES-FIGURINOS-V2.md)
- [Resultados completos por tomada em JSON](RELATORIO-FILTRO-FIGURINO-V2.json)

## Antes de aprovar alguma correção

- [ ] Referência individual completa de Aldric aprovada, com cores e barba travadas
- [ ] Referência individual do vestido palaciano de Elara aprovada, com painel roxo idêntico
- [ ] Comparação visual da nova arte com cada fonte aprovada
- [ ] Revisão de Kael e da variante de rua sem falsas exigências do corpete real
- [ ] Se houver comparação automática de pixel, fornecer máscaras/ROIs realmente verificadas (sem inventar coordenadas)

Aprovação automática **NÃO** foi executada; R2 permanece bloqueada, nenhuma imagem paga, MP4 ou publicação ocorreu nesta rodada.
