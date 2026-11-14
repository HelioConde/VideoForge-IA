# VideoForge-IA — rig 2D real com Three.js + Remotion

> **REGRA CANÔNICA:** [MANUAL PRINCIPAL DE ANIMAÇÃO 2D](MANUAL-PRINCIPAL-ANIMACAO-2D.md) tem precedência sobre este relatório de implementação e todas as notas antigas. Os smoke-tests sintéticos NÃO aprovam personagens reais.

**Situação em 14/11/2026:** motor matemático, renderer ThreeCanvas, contrato de assets e runner GHCR implementados e **testados com sprites sintéticos**. A execução [43580456827](https://github.com/HelioConde/VideoForge-IA/actions/runs/43580456827) passou com 8 testes matemáticos, 5 testes Python e cinco frames reais de Chromium/WebGL em software swangle. **Isso ainda NÃO é a animação definitiva da Anya.** Não há um conjunto aprovado de cabeça/corpo/cabelo separados para as 16 cenas do vídeo Spy × Family. Não foi publicado vídeo no YouTube.

## O padrão correto

- **Corpo** sem cabeça: micro-respiração aplicada ao layer corporal, não ao PNG inteiro como uma placa.
- **Cabeça**: layer rígido independente, inclinação máxima ±2 graus, com pivô no pescoço medido na imagem original. Compartilha a pose neutra na transição de piscada.
- **Olhos**: duas versões da MESMA cabeça, uma aberta e outra fechada, com pixels idênticos fora da região ocular, mantendo franja, cabelo, rosto e transparência. A troca ocorre entre dois PNGs completos e alinhados da cabeça, sem adesivo de pálpebras.
- **Cabelo e roupa/capa**: malha verdadeira de vértices com raiz ancorada e pontas livres, deformação leve e secundária calculada pelo número do frame. A capa é opcional e não pode ser inventada numa cena que não a possui.
- **Braços e itens**: layers independentes apenas quando os sprites já estiverem reconstruídos. IK fica para fase posterior.
- **Transições sem pulo**: posição neutra antes/depois das piscadas e dos cortes; o relógio global nunca é reiniciado abruptamente.
- **Proibido** chamar pan, zoom ou bob de PNG inteiro de animação articulada, duplicar partes separadas ou marcar uma prévia sintética como vídeo oficial.

## Módulos no repositório

- Motor matemático e malha subdividida: motion-remotion/src/rig-three-math.ts
- Renderizador WebGL com ThreeCanvas e BufferGeometry: motion-remotion/src/rig-three-scene.tsx
- Entrada isolada do Remotion: motion-remotion/src/rig-three-index.ts e rig-three-root.tsx
- Validação fail-closed de PNGs, bbox, SHA e pivôs: videoforge/rig_three_contract.py
- Preparação/QA do MP4 com sprites reais: videoforge/rig_three_preview.py
- Pipeline normal de rig real: .github/workflows/rig-three-real-render.yml
- Smoke-test sem arte de canal: .github/workflows/rig-three-smoke.yml
- Container: ghcr.io/helioconde/videoforge-remotion-runner:rig-three-remotion4-v1

**Versões reproduzíveis:** Three.js 0.187.0, React Three Fiber 9.8.2, @remotion/three 4.0.539 e Remotion 4.0.539. O runner contém npm/Chrome/Three pré-instalados: **nenhum npm install durante o render**. A imagem antiga GHCR permanece intacta.

## Manifesto e preparação da arte

O template não aprovado está em modelos/camadas-animadas/rig-three.template.json. O rig real exige um arquivo rig.json e PNGs RGBA recortados da MESMA cena-mãe, com hashes e bbox em coordenadas do canvas original, no diretório correspondente à cena e ao canal.

Etapas artísticas necessárias:

1. Manter o background e a imagem-mãe original como referência.
2. Produzir body-no-head.png reconstruindo pescoço e ombros escondidos.
3. Produzir head-open.png e head-closed.png com imagem e cabelo idênticos fora dos olhos.
4. Extrair hair-front.png e hair-back.png somente se forem animados; RETIRAR essas partes do sprite-base para evitar duplicação.
5. Separar capa, roupa e objetos apenas se existirem na composição e necessitarem movimento.
6. Compor as partes em pose neutra e comparar com a imagem original. Produzir diff/contact sheet; rejeitar discrepâncias, buracos, cabelos duplicados, falhas no pescoço, olhos fora do lugar e oclusão incorreta.
7. Preencher os SHA-256 e o QA de revisão humana. Não declarar aprovação com base somente em PNG RGBA válido.
8. Gerar MP4 por GitHub Actions com --gl=swangle --concurrency=1, validar frames e retornar artifact de revisão, sem publicar.

**Estado do QA:** o contrato Python valida formato, transparência, origem, integridade, bbox, ângulo, raiz fixa, frames de blink e flags de revisão. Um diff numérico automático completo da recomposição neutra ainda precisa ser desenvolvido. As flags de QA visual não podem ser preenchidas como true sem revisão real.

## Aplicação específica à cena 01 de Spy × Family

Já existem imagem-mãe, background separado, sprite geral do personagem e variantes da mesma imagem com olhos abertos/fechados. Ainda **faltam** corpo sem cabeça, cabeça individual nas duas variantes, cabelo separado com pixels ocultos reconstruídos, medidas de pivô e manifesto validado. **Não gerar capa/espada do personagem antigo.**

Sem essas peças, o workflow de malha REAL deve permanecer bloqueado. Não renderizar um simples personagem flutuando como substituto. Só após uma candidata validada para a cena 01 devem ser preparados os mesmos assets das demais 15 cenas.
