# Revisão visual assistida — continuidade C01-P03 V2 / C02-P01 / C02-P02 / C03-P01 (17/11/2026)

**Estado: QA de fontes/SHA aprovado tecnicamente; continuidade visual NÃO aprovada para rig.** A inspeção abaixo é preliminar do assistente, não uma aprovação humana definitiva.

## Fontes e evidência

- [Prancha original de quatro quadros](QA-C02-C03-CONTINUIDADE-IMAGENS.jpg), SHA da prancha `e4759d560f02f601e5f9966b1c57fa3024dd956d8b9ccec22c883558886276af`.
- [JSON de fontes com SHA](QA-C02-C03-CONTINUIDADE-IMAGENS.json), validado pelo [workflow #44084847732](https://github.com/HelioConde/VideoForge-IA/actions/runs/44084847732) (success), **zero chamadas de imagem** e sem sprites por recorte.
- C01-P03 V2, Kael ajoelhado, SHA `bfc1249dc1f83b004b620c333f5aa81689b0ba0c23a3e7573d57c09dcf3539e3`.
- C02-P01, close de Aldric, SHA `0d1f8367c76cdf0c9b63f10071406a567b5a5a10cf799e1aa6c5d814019fa2a0`.
- C02-P02, close de Kael, SHA `a963b04237e6fdd0ff82474e792e15b3cc6bf6a4337e218d595f067593b78bf3`.
- C03-P01, reflexo azul na íris, SHA `b0c416e3c0dd10883e2de37a5c2652ee02030d1f6925ec6f47d9a6d56ade09f3`.
- Quatro fontes com canvas **941×1672** e proveniência intacta. Todas têm `human_visual_approval=false`.

## Inspeção visual da prancha

1. **C01-P03 V2:** o enquadramento cumpre a hierarquia planejada — Kael ajoelhado inferior/primeiro plano, Aldric menor no alto da escada, sem lanças/guardas indevidos. Ainda comparar o acabamento da armadura com a Bíblia.
2. **C02-P01 / Aldric:** coroa, cabelos longos brancos, barba, peles e cores vinho/dourado mantêm a família de design geral. **Possível descontinuidade da coroa e gola**: no close, a coroa aparece maior, com múltiplas gemas vermelhas e moldura mais ornamentada, e a gola fica alta e branca/dourada. Em C01-P03 a cabeça/coroa estão muito menores e não permitem julgamento definitivo; inspecionar mestre da Bíblia em resolução nativa antes de editar.
3. **C02-P02 / Kael:** corte de três quartos, cabeça baixa, armadura e capa vinho, olhos baixos e tensão contida atendem à intenção dramática. Existem marcas faciais discretas, mas o estilo de cabelo e bordas ainda precisa de comparação canônica.
4. **C03-P01 / Kael:** o reflexo azul aparece dentro dos olhos, porém a arte mostra **grande parte do rosto, nariz e boca**, não um enquadramento *extreme close-up / macro de íris* como planejado. Além disso, as **marcas vermelhas no rosto são maiores/muito mais evidentes** que em C02-P02, apesar de ser uma ação contínua. A íris aparece com reflexo azul em ambos os olhos; verificar se o match cut deve privilegiar um olho.
5. **C03-P02 / quarto:** antes da geração, o plano foi corrigido porque carregava refs medievais erradas. Agora exige o quarto gamer moderno, monitor azul e Kael casual V2. É o **segundo quadro de uma transição de montagem**, não um split screen; C03-P01 será o primeiro quadro.

## Decisões e próximos passos

- **Não promover C03-P01 para rig** sem corrigir o enquadramento e a continuidade dos ferimentos por nova geração/edição controlada do proxy, se a revisão do proprietário confirmar. Preservar PNG original e SHA.
- **Não afirmar defeito conclusivo de identidade em Aldric** apenas pela miniatura; comparar com referência-mestre a mesma peça (coroa, gola e broches), e corrigir se necessário.
- Prosseguir gerando as demais imagens-mãe do episódio, mantendo as imagens atuais como candidatas. **Não gerar partes do rig por recorte local**; a mãe aprovada + Bíblia alimenta os pedidos de PNGs independentes ao proxy.
- Sem `human_visual_approval`, `rig_ready`, `mp4_generated` ou `youtube_uploaded`.

**Resumo QA:** `sha_source_qa=passed`, `artistic_continuity_qa=needs_corrections`, `assistant_preliminary_review=done`, `owner_review=pending`.
