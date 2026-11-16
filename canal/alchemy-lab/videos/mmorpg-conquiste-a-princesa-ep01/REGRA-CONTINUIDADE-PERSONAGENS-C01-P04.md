# Regra obrigatória — consistência de personagens após C01-P04

**Referência visual aprovada:** [C01-P04 — imagem original do GitHub](assets/geracoes/production-art-request/43965460068/c01-p04-imagem-inicial-v3.png). O responsável elogiou sua aparência em 16/11/2026 e exigiu que as próximas imagens mantenham **as mesmas características visuais dos personagens**.

- **Registro SHA:** [CONTINUIDADE-VISUAL-APROVADA-C01-P04.json](CONTINUIDADE-VISUAL-APROVADA-C01-P04.json). SHA original `605ccd361ad9a867eb8b92948010fdbb7d87a031d8b3601c663d815917b1b6cc`, 941×1672 px. A imagem aprovada é a referência de **aparência, figurino visível, paleta e identidade de personagens** do tribunal.
- **Obrigatório no gerador:** usar `/v1/images/edits` com **bytes originais exatos do PNG** anexados. Validar SHA + manifesto + dimensões + elenco. Jamais recorrer à geração somente por texto para personagens que aparecem na âncora. O código está em `videoforge/dorama_continuity.py`, reutilizado por `videoforge/production_art.py`.
- **Kael:** mesmo cabelo, rosto, roupa/capa vinho, ombreira com detalhes dourados/azuis, marcas de cansaço. **Aldric:** mesmo rosto, barba grisalha volumosa, coroa e traje. **Guardas:** os mesmos elmos, armaduras, luvas e lanças — com lado/espaço coerentes.
- **Estilo canônico:** pintura digital 2D fantasia anime semirrealista cinematográfica. Proibido alternar aleatoriamente para foto realista, CGI 3D, arte chibi/manhwa plano ou figurino diferente.
- **Geografia:** mesmo trono, vitrais, degraus, luz e direção dos objetos; mudar o **ângulo de câmera** narrativamente, não apenas ampliar/cortar uma imagem ampla.
- **Cena com personagens ausentes da referência:** gerar nova âncora específica antes de usá-los. **Elara não aparece em C01-P04**; não usar essa imagem como referência de sua identidade.
- **Nova tomada C01-P05:** close das mãos enluvadas dos guardas segurando duas lanças cruzadas; devem manter a mesma aparência da âncora sem duplicar armas, membros ou personagens.
- **Se o novo quadro desviar:** marcar `EVIDENCIA_INSUFICIENTE` ou `REVISAR` e registrar o defeito concreto, sem aceitar por SHA válido. Não alterar o PNG original aprovado nem fingir que um teste cromático comprova semelhança facial.

**Importante:** aprovação da referência visual não equivale à aprovação de todas as máscaras antigas de Aldric e Elara, nem libera publicação. As rejeições anteriores permanecem arquivadas. A aprovação da referência **evita refazer toda a análise antiga a cada plano**: reutilizar uma âncora SHA estável e revisar somente desvios detectados.

**Fluxo:** plano oficial → escolher elenco → validar que o elenco aparece na âncora → anexar a imagem original → gerar novo ângulo no GitHub → arquivar PNG/SHA → comparar com âncora → separar camadas → rig/Remotion.
