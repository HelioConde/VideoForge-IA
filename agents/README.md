# Estúdio multiagente VideoForge-IA

Esta arquitetura é **documental e de contratos**, não cria por si só 12 processos de IA em execução. O orquestrador/workflows existentes devem ser integrados e testados antes de automatizar dispatch paralelo.

## Papéis
- [Planejamento e distribuição](./diretor-geral/AGENT.md) (`diretor-geral`)
- [Roteiro e diálogo](./roteirista/AGENT.md) (`roteirista`)
- [Blocking e continuidade](./diretor-cenas/AGENT.md) (`diretor-cenas`)
- [Bíblia Visual](./diretor-arte/AGENT.md) (`diretor-arte`)
- [Imagens-mãe](./gerador-visual/AGENT.md) (`gerador-visual`)
- [Assets RGBA](./separador-camadas/AGENT.md) (`separador-camadas`)
- [Malhas e pivôs](./especialista-rig/AGENT.md) (`especialista-rig`)
- [Movimento](./animador/AGENT.md) (`animador`)
- [Cinematografia](./diretor-camera/AGENT.md) (`diretor-camera`)
- [Som](./especialista-audio/AGENT.md) (`especialista-audio`)
- [Render e empacotamento](./montador/AGENT.md) (`montador`)
- [QA independente](./supervisor-qa/AGENT.md) (`supervisor-qa`)

## Fluxo
Diretor geral -> roteiro -> direção de cenas -> direção de arte -> geração visual -> separação -> rig/animação/câmera -> áudio/montagem -> supervisor QA -> revisão humana.

Trabalhos sem dependência podem rodar em paralelo. Cada entrega deve declarar `task_id`, `owner`, `inputs`, `input_shas`, `outputs`, `output_shas`, `status`, `evidence`, `reviewer` e `blocked_by`. O supervisor não é o produtor do asset avaliado.

## Regras prioritárias
- Ler `AGENTS.md`, regras do canal e checkpoint do vídeo antes de agir.
- O EP01 C07/C08 V2 continua em revisão humana, não aprovado.
- Não repetir chamadas ao proxy se asset versionado e SHA íntegro já existem.
- Não separar mãos independentes na C01-P04; não fingir rig com PNG inteiro.
- Não executar publicação no YouTube; apenas após autorização explícita e gates específicos.
- Não alterar workflows de produção existentes nesta migração documental.
