# Bíblia visual e de animação — A Missão Impossível (EP01)

## Direção imutável
**2D de manhwa de fantasia romântica, cinematográfico, pintura digital detalhada**, silhuetas e anatomia coerentes, cores elegantes e faces expressivas. O mesmo traço, render de pele, proporções, cores de olhos e cabelo em TODAS as cenas (inclusive mundo contemporâneo e flashback). Proibido alternar realismo fotográfico, 3D render, anime genérico e desenhos distintos. Ficção original: sem semelhança deliberada com atores, séries, jogos ou personagens protegidos. Composição vertical 1080×1920, 30fps, paleta azul profundo, prata, âmbar e vinho escuro.

## Personagens canônicos
- **Kael**, 23 anos, homem adulto: rosto oval e levemente anguloso, sobrancelhas retas expressivas, olhos âmbar, cabelo preto ondulado curto e mechas soltas na testa. Na vida real: camiseta cinza escuro. No reino: camisa creme, jaqueta curta grafite com costuras azuis discretas, calça marrom, botas simples, pequena bolsa no cinto; sem capa, espada ou armadura. Emoções: pânico contido, incredulidade, coragem improvisada. Em TODAS as cenas de Arken, usar exatamente a mesma roupa e proporções.
- **Princesa Elara**, 21 anos, mulher adulta: rosto delicado próprio, olhos violeta acinzentados, cabelo longo preto com brilho azulado, uma mecha presa com acessório prateado em forma de flor. No trono: vestido azul meia-noite com bordados prateados e uma pequena tiara; no flashback do mercado e beco: o MESMO vestido oculto por manto com capuz azul escuro, sem mudança de rosto, olhos ou penteado. Ela não está apaixonada no começo; é perspicaz, corajosa e possui objetivo político próprio.
- **Rei Aldric**, 55 anos: porte imponente, barba curta com fios grisalhos, cabelo preto-grisalho penteado para trás, olhos de aço, coroa dourada estreita, túnica bordô e manto negro sobre ombros; severidade sem caricatura.
- **Guardas reais**: elmos e placas de aço prateado, estandarte azul e prata, aparência idêntica entre cenas do mesmo destacamento.
- **Assassinos mascarados**: roupas escuras discretas, sem brasão real. Diferenciar claramente dos guardas para que a trama não pareça incoerente.

## Mundo e cenários
- **Reino de Arken**: arquitetura medieval fantástica europeia estilizada no desenho manhwa, pedra azul-acinzentada, detalhes dourados, flor prateada como símbolo real. Consistência de escala, perspectiva, horário e iluminação entre planos do mesmo local.
- **Salão do trono**: rei no centro em plataforma elevada; princesa à direita do rei (à esquerda na imagem se a câmera olha de frente); Kael ajoelhado ao centro inferior; dois guardas às laterais. Manter lado, luz e figurinos consistentes. Revelar a princesa deliberadamente só na cena C11.
- **Mercado e becos**: casarões de pedra, bancas de madeira, luz de tarde, objetos com perspectiva. Não substituir por mercado genérico diferente a cada quadro.
- **Quarto contemporâneo**: mesma estética 2D que o reino, luminária e monitor azul; tela de jogo sem interface de jogo/marca comercial existente.
- **UI RPG**: holograma retangular azul translúcido, tipografia branca nítida, bordas finas e pequenos ícones originais. Somente Kael vê os painéis. Textos exatamente iguais ao roteiro; atenção especial à missão “CONQUISTE O CORAÇÃO DA PRINCESA”.

## Contrato da animação por cena
Ler antes de tudo `docs/MANUAL-PRINCIPAL-ANIMACAO-2D.md`. Para cada cena: salvar (1) imagem-mãe; (2) background reconstruído sem partes móveis; (3) PNGs RGBA verdadeiros da mesma imagem-mãe; (4) torso/body-no-head e underlays ocultos reconstruídos; (5) head-open/head-closed idênticos fora dos olhos; (6) hair-back/hair-front, peças de roupa e membros/objetos conforme a cena; (7) rig.json com SHA, bbox, pivôs e z-index; (8) diff da recomposição em pose neutra; (9) QA de frame e transição. Sem assets, marcar `pipeline_pendente`.

Gestos que PRECISAM de articulação interna real:
1. Kael abaixa a cabeça, mas desvia **somente os olhos** de rabo de olho para a princesa; preservar respeito/continuidade de direção de olhar, sem transparência facial.
2. Kael pisca e inspira com tensão; cabeça no pivô de pescoço ±2 graus no MVP; corpo e mandíbula conforme peças disponíveis.
3. Elara reage com olhos e sobrancelhas, segura a mão dele no flashback, dá um passo e fala diante do pai; nunca simular corrida ou passo animando PNG inteiro.
4. Cabelos, vestido, manto e jaqueta reagem suavemente ao movimento e vento por malhas com raízes fixas, sem atravessar braços ou pele.
5. Objetos (broche, bolsa, carrinho, armas de guardas) separados e relacionados às mãos/oclusões.
6. UI RPG como overlay DE HUD, não é substituta de personagem animado.

Motor: Three.js + React Three Fiber + @remotion/three/ThreeCanvas no Remotion 4; tempo derivado só de useCurrentFrame(); swangle no runner; reutilizar GHCR prebuilt. FFmpeg só para áudio/QA. Não inventar imagens “de outra cena” para os recortes. Nunca reaproveitar visual de capa vermelha/espada de experimentos anteriores. QA fail-closed contra buracos, franjas recortadas, duplicação, peças com alfa indevido, estilo inconsistente, tremor e salto no corte.

## Checklist de arte antes de renderizar
- Cada personagem idêntico da primeira à última cena (paleta, rosto, cabelo, acessórios e altura).
- A princesa encapuzada e a princesa do trono são inequivocamente a mesma pessoa.
- O salão conserva posição do rei, da princesa e dos guardas.
- Rosto opaco em todos os quadros, inclusive piscada e olhar lateral.
- Camadas e pivôs respeitam partes ocultas reconstruídas, sem halos de recorte.
- Interface não encobre o olhar lateral, o rosto da princesa ou as legendas.
- Narração e trilha próprias/licenciadas; não usar OST de dorama ou jogo.
- Human review não pode ser marcada como aprovada sem inspeção; sem MP4 oficial até rig e QA completos.
