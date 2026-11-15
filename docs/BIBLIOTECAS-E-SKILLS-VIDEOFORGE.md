# Bibliotecas e skills reutilizaveis — VideoForge IA (15/11/2026)

**Meta:** acelerar o desenvolvimento dos videos no GitHub sem perder identidade visual, QA, continuidade nem reimplementar projetos prontos. **Escolha:** reutilizar o motor e dependencias ja existentes do repo, aprender de skills oficiais, nao instalar sistemas concorrentes e nao introduzir custos.

## Catalogo aprovado para uso no EP01

| Tecnologia | Origem | Situacao no repo | Uso pratico | Restricao |
|---|---|---|---|---|
| Remotion 4 | https://github.com/remotion-dev/remotion | Presente em `motion-remotion/package.json` | Timeline, frames, Sequence, audio, 9:16 | render so depois do gate de QA |
| @remotion/three | https://github.com/remotion-dev/remotion/tree/main/packages/three | Instalado | ThreeCanvas com tempo Remotion | render reproducivel sem GPU (swangle) |
| Three.js | https://github.com/mrdoob/three.js | Instalado | vertices, malhas, materiais, pivôs reais | sem animacao de frame global |
| React Three Fiber | https://github.com/pmndrs/react-three-fiber | Instalado | componentes de personagem, sprite, prop | reaproveitar CharacterParts/RigidSprite |
| Remotion Agent Skills | https://github.com/remotion-dev/skills/tree/7e541aa4d7361dfaca0780a565a47307eb7bdfbb | **Integrado como referencias nas 3 skills locais** | orientar agentes sobre 3D, cinematografia, composicao, audio e render | nao executar `npx latest` ou copiar upstream sem licenca |
| Rigby2D | https://github.com/jaisurya-dev-art/rigby2d | **Somente pesquisa; NAO instalado** | estudar exportacao de bones/mesh se compatibilidade comprovada | nao substituir engine Remotion/Three nem adicionar custo |
| FFmpeg / FFprobe | https://github.com/FFmpeg/FFmpeg | Runner ja utiliza | sondagem, multiplexacao, QA tecnico | **nunca** animar um PNG chapado como falso rig |

## Skills prontas e descobriveis pelos agentes

- `.agents/skills/videoforge-dorama-remake/SKILL.md`: direcao, backlog, continuidade e fluxo automatico.
- `.agents/skills/videoforge-rig-2d-three/SKILL.md`: geometria de rig real, pelo e tecido, pivos, exemplo C01-P02.
- `.agents/skills/videoforge-qa-and-checkpoint/SKILL.md`: QA tecnico e visual, evitar retrabalho, persistir evidencias.

As skills locais usam instrucoes originais adaptadas ao projeto e **apontam** ao codigo fonte oficial `remotion-dev/skills` no commit fixo `7e541aa4d7361dfaca0780a565a47307eb7bdfbb`. Evitar instalar o ultimo `remotion-dev/skills` em CI: o upstream pode usar APIs de versao superior ao `package-lock.json` que a producao tem. Verificar licenciamento antes de copiar codigo externo e nao instalar ferramentas por impulso.

## Componentes reutilizados diretamente

- `motion-remotion/src/rig-three-scene.tsx`: `RigidSprite`, `DeformableSprite`, `CharacterParts`.
- `motion-remotion/src/rig-three-math.ts`: malha deformavel, piscada, cabeca e corpo com quadros puros.
- `motion-remotion/src/remake-sword-motion.ts` e `remake-sword-rig.tsx`: **nova biblioteca original reutilizavel** para desembainhar espada com mao em pivo e bainha fixa. Nenhum grafico ou PNG gerado sem fonte.
- `videoforge/remake_starter.py`: compila os 37 planos em tarefas deterministicas com perfil de rig, imagens/partes requeridas, dependencias, `task_fingerprint` e workflow candidato. Nao despacha API paga nem fabrica aprovacao.
- `videoforge/remake_autopilot.py`: escolhe proxima etapa pela evidencia e atualiza checkpoint.

## Ordem de implementacao

1. **C01-P01:** 60 frames pretos pelo Remotion; so audio original/licenciado, sem gastar imagem e sem declarar video completo.
2. **C01-P02:** usar componente de espada real, separando PNGs **blade, sheath, hand e underlay** da imagem-mae com referencia canônica aprovada. Regular distancia/angulo/pivo usando a arte real, nao numeros inventados de QA.
3. **C01-P03/C01-P04:** reutilizar `CharacterParts` + malhas de capa e cabelo, guardas com dois rigs e lanças em pivôs distintos; criar underlays e QA. Nunca restaurar rig V5 como arte final do remake automaticamente.
4. Repetir perfis para os planos restantes, sempre com arte propria por perspectiva, SHA, QA tecnico, revisao humana e audio.
5. Entrega final somente quando o compositor Remotion aceitar todo manifesto, todos os assets reais e aprovacao para producao; **nada publicado no YouTube por padrao**.

## Seguranca e desempenho

Bibliotecas atuais sao suficientes para iniciar. Nao adicionar `rigby2d`, PixiJS, Spine, Live2D, `fluent-ffmpeg` ou motores duplicados sem uma razao mensuravel; `fluent-ffmpeg` esta descontinuado. Nao atualizar dependencias nem rodar instalador remoto durante render. A qualidade tem prioridade sobre teto editorial de imagens, **mas provedor pago, gastos e publicacao exigem autorizacao distinta**.
