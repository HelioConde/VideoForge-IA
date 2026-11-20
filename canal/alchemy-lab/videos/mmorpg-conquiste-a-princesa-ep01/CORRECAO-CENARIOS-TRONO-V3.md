# EP01 — Correção V3: geografia da perseguição e rei sentado

**Feedback do criador em 20/11/2026:** sete capturas demonstraram repetição excessiva do mesmo beco durante corrida, encontro, carroça e fuga. Na corte, o rei desaparece entre tomadas ou muda de sentado para em pé sem transição. A revisão V2 dessas tomadas foi reprovada visualmente.

## Referências de localização a criar antes de refazer as imagens

| Código da Bíblia Visual | Lugar | Marco visual obrigatório | Proibição |
|---|---|---|---|
| `biblia-largo-encontro-arken-v3` | Largo do Mercado, após esquina | Praça e poço circular, tendas verdes e azuis | Não reutilizar ponte/estandarte/lampião do beco |
| `biblia-gargalo-servico-arken-v3` | Portão de serviço, alguns passos a leste do mercado | Armazéns ocre e passagem estreita, portão de ferro | Não reutilizar ponte/estandarte/lampião do beco |
| `biblia-escadaria-saida-arken-v3` | Escadaria curva até o pátio superior | Pedra clara, heras azuis, muros e jardim | Não reutilizar ponte/estandarte/lampião do beco |

Todos são **backgrounds sem pessoas e sem carroça**. A geração de mães V3 DEVE usar a imagem real arquivada por SHA do local correspondente, além das referências visuais dos personagens/objetos. Não basta renomear o mesmo quadro do beco.

## Tomadas corrigidas

- **C01-P03:** Kael ajoelhado e Aldric sentado no trono, usando a arte C01-P04 já aprovada como âncora. Nada de rei de pé.
- **C01-P04:** preservar integralmente os pixels e SHA aprovados; rei sentado.
- **C01-P05:** close de lanças/guardas, mas com rei sentado ao fundo. Ele não desapareceu, só houve corte de câmera. Segurar a base da lança corretamente.
- **C02-P01 e C02-P02:** manter artes existentes em que o rei permanece sentado; se o enquadramento for fechado, não inferir mudança de pose.
- **C07-P01 e C07-P02:** fuga e perseguição no antigo beco; estas duas fontes permanecem para referência.
- **C07-P03:** entrada no Largo do Mercado, sem carroça, primeiro encontro com Kael.
- **C07-P04:** conversa PARADA no Largo do Mercado; sem carrinho e sem guardas.
- **C08-P01:** mostrar a descoberta do carrinho encostado à parede direita do portão de serviço; Kael e carrinho apenas.
- **C08-P02:** Kael move e gira o mesmo carrinho SOZINHO, sem perseguidores próximos nem mãos soltas.
- **C08-P03:** imagem somente da **carroça atravessada bloqueando o beco**, sem NENHUM personagem. O efeito causal do bloqueio deve ser compreensível.
- **C08-P04:** Elara foge pela escadaria curva em outra parte da cidade; sem carroça, mesma capa e identidade.
- **C08-P05:** Kael a alcança no patamar da escadaria; não segura o braço dela sem motivo.
- **C09-P01 e C09-P02:** agradecimento e despedida no pátio superior, com o mesmo background da fuga pós-barricada, evitando o teletransporte de volta ao primeiro beco.

**Geografia:** beco da fuga → esquina e mercado → portão de serviço e carroça → escadaria → pátio superior. As mesmas localizações consecutivas podem compartilhar cenário, mas mudar de fase exige arquitetura inequivocamente diferente. A câmera só ajusta composição, não deve disfarçar erros de geografia ou postura.

## Implementação e status

- Plano estruturado: `CORRECAO-CENARIOS-TRONO-V3.json`.
- Gerador: `videoforge.ep01_continuity_v3`. **14 novas gerações requeridas**: três backgrounds e 11 mães versionadas, em 14 Actions filhas, no máximo uma chamada de imagem por execução. Cada original é arquivado junto ao SHA e manifesto.
- Fila: `.github/workflows/ep01-continuity-v3.yml` e `scripts/ep01_continuity_v3_queue.py`: primeiro backgrounds, depois imagens-mãe; não repetir chamadas pagas de resultado incerto.
- Render de revisão: `.github/workflows/ep01-continuity-v3-review.yml`. Disponibilizar **um MP4 de 42 tomadas/163 s** com índice e QA, só depois das 14 fontes estarem arquivadas. Nenhum MP4 V3 foi declarado pronto antecipadamente.
- Versão V2 e imagem C01-P04 aprovada permanecem intactas para auditoria; **não reescrever/autorizar rig, voz, legenda final ou YouTube**.

A versão V3 é uma nova candidatura artística, não aprovação visual. Entregar ao criador o MP4 para verificar se geografia, carrinho e posição do rei realmente foram corrigidos.
