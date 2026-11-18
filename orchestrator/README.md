# Contratos do orquestrador

`tasks.json` é a fila declarativa inicial, não um executor ativo. `dependencies.json` declara gates; `checkpoints.json` registra estado de migração. Integração com GitHub Actions exige implementação e testes separados.

## Estados
`pending`, `ready`, `running`, `blocked`, `needs_review`, `approved`, `rejected`, `failed`. `approved` para arte/continuidade requer evidência de revisão humana; sucesso de Action significa apenas QA técnico.

## Idempotência
Chave de geração = SHA256 de prompt normalizado + SHA das referências + modelo + parâmetros + versão do plano. Antes do proxy, verificar registro persistido e integridade do arquivo; corrida concorrente exige lock por chave. Nunca inferir geração por mera presença de nome de arquivo.

## Ownership
Um responsável por tarefa, um revisor diferente. Registrar run ID, artifact URL real, SHA e razão de falha. Reabrir apenas a tarefa defeituosa, preservando assets aprovados.
