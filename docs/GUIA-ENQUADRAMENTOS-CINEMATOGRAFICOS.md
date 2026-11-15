# Direção cinematográfica por planos — VideoForge-IA

Este guia complementa o [Manual Principal de Animação 2D](MANUAL-PRINCIPAL-ANIMACAO-2D.md), que permanece superior para rig, separação, QA e Remotion.

## Objetivo

Em doramas, anime e histórias narrativas, **uma cena não deve resultar em uma sequência de pôsteres iguais**. O programa precisa decidir **o que a câmera está contando em cada corte**. Um plano amplo estabelece geografia; um close mostra conflito; um olhar revela subtexto; um contraplano mostra reação; um insert isola uma espada, mão, jóia, carta ou outro objeto.

O sistema deve planejar as **tomadas cinematográficas antes de solicitar as imagens-mãe**. Uma cena pode ter 1, 2, 3 ou mais tomadas, conforme o roteiro, sem teto artificial. Se 37 planos são necessários, eles exigem 37 decisões cinematográficas, não 14 fotos gerais repetidas.

## Linguagem das tomadas

| Tipo | Enquadramento | Uso narrativo | Lente virtual sugerida |
|---|---|---|---|
| **Plano de estabelecimento** | salão, rua, palácio ou ambiente completo | mostrar lugar, escala, geografia e posições | 24–35 mm |
| **Plano médio** | torso/cintura e gesto relevante | falar, interagir e manipular objetos | 40–60 mm |
| **Close-up do rosto** | rosto expressivo ocupa a imagem | mostrar medo, dúvida, raiva, coragem, emoção | 70–100 mm |
| **Close extremo dos olhos** | pupilas, sobrancelhas, cílios | reconhecimento, decisão secreta, lágrimas, choque | 90–120 mm |
| **Sobre o ombro (OTS)** | personagem parcialmente em primeiro plano, outro em foco | revelar perspectiva subjetiva ou confronto | 35–70 mm |
| **Insert de mãos/props** | mãos, bainha, espada, broche, itens | contar uma ação por um detalhe real | 70–120 mm |
| **Contraplano de reação** | alternância entre quem fala e quem escuta | construir tensão e emoção sem repetir composição | 70–100 mm |
| **Ângulo baixo** | eixo da câmera abaixo do personagem | mostrar autoridade, vulnerabilidade ou ameaça | 28–50 mm |
| **Ação/travelling** | visão lateral ou em acompanhamento | acompanhar corrida, ataque, fuga, objeto em movimento | 28–50 mm |
| **Match cut** | composição encadeada por forma/cor | ligar dois momentos ou tempos diferentes | variável |

A lente é **intenção de composição**, não uma transformação de zoom que substitui nova arte. Profundidade de campo, luz e eixo de 180° devem ser tratados como parte da identidade de cada tomada.

## Regra de continuidade: mesma identidade em todos os ângulos

Cada personagem deve ter um **character lock**: rosto, proporções, olhos, cicatrizes, cabelo, cor de pele, acessórios e figurino por local/época. Para cada tomada, fornecer essa referência real e a referência do cenário, sem inventar novos cabelos, roupas ou rostos para deixar o enquadramento bonito.

A nova tomada usa **sua própria imagem-mãe**, com enquadramento e iluminação coerentes com o plano anterior. Seus PNGs de fundo e partes móveis derivam da própria mãe, não da imagem ampla de outra câmera. Se o close mostrar rosto antes não visível, não inventar olhos sobre a nuca de um personagem de costas. Se o plano precisa de contra-plano, a arte de contra-plano deve ser produzida e aprovada quando o usuário autorizar novas imagens.

**Não confundir personagem visualmente semelhante com personagem idêntico.** Conferir e registrar referências por SHA e versão da bíblia. Uma referência nova aprovada pode substituir outra depois de migração explícita; nunca misturar versões de figurinos entre planos.

## Regras de roteiro e edição

1. Começo pode ter plano amplo ou uma única arte de abertura com título, mas **nem todos os quadros devem ter título, personagem inteiro e todos os coadjuvantes**.
2. Conversa: alternar close do falante, close do ouvinte, OTS e dois planos; preservar geografia, linha do olhar e posição de luz.
3. Suspense: rosto em close, olhos em extremo close, objeto em insert e silêncio antes de revelar o acontecimento; rosto com expressão inteligível, e não apenas um zoom.
4. Heroínas e personagens secundários têm closes de reação próprios quando o roteiro pede; o modelo não deve inventá-los em cenas em que ainda estão ocultos.
5. No tribunal de Arken, **a princesa só pode ser revelada como princesa no momento da revelação C12**, não surgir antecipadamente atrás do rei nas tomadas C01 e C02.
6. Texto legível, títulos, menus RPG, HUD, legendas e notificações são **camadas do Remotion**. Não deixar o modelo pintar UI em todas as imagens.
7. 1024×1536 (origem 2:3) para 1080×1920 (saída 9:16): compor com safe area vertical e recorte lateral; nunca esticar rosto/corpo.
8. Movimento de câmera pode unir tomadas; porém **não substitui rig de personagens**. Rosto, olhos, mandíbula, mãos, cabelo e tecido exigem sprites, malhas, pivôs, underlays e QA do manual.
9. Cada tomada registra `shot_id`, `scene`, `shot_type`, `primary_focus`, `lens_mm`, `start_frame`, `end_frame_exclusive`, `characters`, `hud_policy`, `source_art_status` e `approved_for_render`.

## Fluxo do programa

`roteiro.json` → `direcao-rig-remotion.json` → `direcao-cinematografica-planos.json` → **QA textual sem IA** → cada `shot_id` é enviado à geração de **imagem-mãe específica** com a mesma referência canônica (quando autorizado) → separar fundo e sprites RGBA → reconstruir regiões ocultas → QA neutro → rig ThreeCanvas → compor os planos no Remotion → QA audiovisual.

A etapa de direção é implementada em `videoforge/cinematic_direction.py`. O gerador atual `videoforge/production_scenes.py` aceita `--shot-id C12-P01` para criar uma imagem-mãe específica, sem substituir os formatos anteriores. O workflow `production-scene-by-request.yml` aceita a mesma opção em execução manual e nos pedidos JSON.

### Episódio exemplo

Em `canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/`, o plano contém **37 tomadas, incluindo 12 closes de rosto/olhos, cinco OTS e quatro planos gerais**. `C01-P01` é preto absoluto e não pode solicitar uma imagem. `C02-P01` é close do rei; `C03-P01` é extremo close dos olhos de Kael; `C12-P01` é olhar de rabo de olho com cabeça imóvel; `C12-P03` é reação da princesa; `C14-P03` é reação final de Kael. O plano oficial fixa posição, elenco e duração, e o novo planejamento fixa **câmera e emoção**.

**Histórico:** o episódio possuía o bloqueio `SEM-GERACAO-NOVAS-IMAGENS.lock` de 14/11, arquivado em 15/11 após autorização explícita do remake. **Somente a produção de novas imagens do remake foi autorizada editorialmente**, sem autorizar publicação ou custos externos sem aprovação. Os visuais mais recentes aprovados na conversa divergem da bíblia antiga (Kael/capa; Elara/cabelo/vestido): a identidade definitiva depende de aprovação da referência e incorporação dos arquivos originais ao GitHub. Nunca assumir que imagens da conversa estão disponíveis no repositório sem conferência.
