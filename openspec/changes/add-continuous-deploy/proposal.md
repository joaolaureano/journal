# Proposal

## Why

Mudar uma fonte no `journal.toml` ou corrigir o código exige rodar `build.sh` e `tofu apply` na máquina do João, e nada roda os testes fora dela. O estado do OpenTofu só existe em `deploy/terraform.tfstate`, na mesma máquina: perdê-la é perder o controle do que está na AWS.

## What Changes

- GitHub Actions: a cada push e pull request, `ruff` e `pytest`; num push na `main`, empacota com `deploy/build.sh` e publica o código na Lambda (`update-function-code`), assumindo um papel por OIDC no ambiente `production`. Sem a variável `AWS_DEPLOY_ROLE_ARN`, a publicação é pulada (forks continuam só com testes).
- `deploy/ci.tf`: papel `${name}-deploy-ci`, criado só quando `github_subject_prefix` é informado, que confia no provedor OIDC do GitHub já existente na conta e só pode trocar e ler o código da função. Usa o mesmo `permissions_boundary` dos outros papéis.
- Infraestrutura continua sendo `tofu apply` local; o CI só publica código e configuração.
- Estado remoto: um bucket S3 versionado guarda o estado, configurado em `deploy/backend.tf` (fora do git) a partir do `backend.tf.example`; `terraform.tfvars` também fica fora do git.

## Impact

- `.github/workflows/ci.yml`, `deploy/ci.tf`, `deploy/variables.tf`, `deploy/outputs.tf`, `deploy/README.md`, `.gitignore`, spec `aws-deploy`.
