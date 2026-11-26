# Proposal

## Why

A conta AWS passa a ter um único teto para os papéis dos projetos: o boundary `project-boundary`, que libera só recursos com o prefixo da tag `Project` do papel (ABAC). A automação local (papel `agent`) só consegue criar papéis com esse boundary, e a conta só opera em `us-east-1`.

## What Changes

- Variável `permissions_boundary` (ARN, padrão nulo) aplicada aos papéis da Lambda e do Scheduler. Sem ela, nada muda para quem faz fork.
- Região padrão `us-east-1` (antes `sa-east-1`), como os outros projetos da conta; o CloudFront é global, então a latência do site não muda.
- Os nomes já seguem o prefixo `var.name` (bucket `journal-site-*`, função `journal-build`, log group `/aws/lambda/journal-build`) e os papéis já levam a tag `Project` pelas `default_tags`, que é o que o boundary exige.
- README do deploy: como passar o boundary.

## Impact

- `deploy/variables.tf`, `deploy/main.tf`, `deploy/backend.tf.example`, `deploy/README.md`, spec `aws-deploy`.
