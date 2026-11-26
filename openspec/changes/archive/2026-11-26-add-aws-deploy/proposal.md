# Proposal

## Why

Levar o journal para a AWS: uma edição por dia às 8h de São Paulo, publicada num bucket S3 e servida pelo CloudFront, dentro do free tier.

## What Changes

- Novo armazenamento `s3` (`S3Storage`): mesma porta do local; `Content-Type` por extensão e `Cache-Control` curto para páginas que mudam a cada edição e longo para edições.
- Handler da Lambda (`journal.aws_lambda.handler`) reaproveitando o build da CLI (`journal.cli.run`); `JOURNAL_BUCKET` troca o armazenamento pelo bucket.
- `deploy/template.yaml` (SAM): bucket privado com versionamento (30 dias), CloudFront com OAC, Lambda arm64 Python 3.12, EventBridge Scheduler `cron(0 8 * * ? *)` em `America/Sao_Paulo`, logs por 14 dias.
- `deploy/build.sh` empacota em `build/`; `deploy/README.md` com o passo a passo.
- Extra opcional `journal[aws]` (boto3).

## Capabilities

### New Capabilities
- `aws-deploy`: armazenamento S3, handler da Lambda e infraestrutura.

### Modified Capabilities
- `journal-config`: tipo de armazenamento `s3`.

## Impact

- `adapters/s3.py`, `aws_lambda.py` (novos), `cli.py`, `config.py`, `pyproject.toml`, `uv.lock`, `deploy/`, README, testes.
- O deploy em si roda com as credenciais do João (`sam deploy`); nada é criado na AWS por esta mudança.
