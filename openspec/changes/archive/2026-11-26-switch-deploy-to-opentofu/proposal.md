# Proposal

## Why

O João usa OpenTofu; manter uma ferramenta só de infraestrutura como código.

## What Changes

- `deploy/template.yaml` (SAM) sai; entram `deploy/*.tf` (OpenTofu, providers `aws` e `archive`) com os mesmos recursos: bucket privado versionado, CloudFront com OAC, Lambda arm64 Python 3.12 empacotada de `build/`, EventBridge Scheduler 08:00 `America/Sao_Paulo`, logs 14 dias.
- Permissão `s3:ListBucket` explícita para a Lambda (sem ela um objeto inexistente responde 403, não 404).
- Estado local por padrão; `backend.tf.example` para S3.
- `deploy/README.md` reescrito para `tofu init` / `tofu apply`.

## Impact

- `deploy/`, `.gitignore`, spec `aws-deploy`.
