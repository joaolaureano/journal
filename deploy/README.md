# Deploy na AWS

Uma Lambda agendada (EventBridge Scheduler, 8h de São Paulo) gera a edição do dia e grava o
site num bucket S3 privado com versionamento; o CloudFront serve o site. Tudo cabe no free tier
para uma execução por dia.

```
EventBridge Scheduler ──(8h, America/Sao_Paulo)──> Lambda (journal.aws_lambda.handler)
                                                     │  busca as fontes
                                                     ▼
                         CloudFront ──(OAC)──> S3: index.html, edicoes/, editions.json, seen.json
```

## Pré-requisitos

- Conta AWS e credenciais configuradas (`aws configure` ou `aws sso login`)
- [OpenTofu](https://opentofu.org/docs/intro/install/) 1.6 ou mais novo
- [uv](https://docs.astral.sh/uv/)

## Primeiro deploy

```sh
./deploy/build.sh            # empacota em build/ (precisa existir antes do plan)
cd deploy
tofu init
tofu apply                   # mostra o plano e pede confirmação
```

No fim, `site_url` é o endereço do jornal. O CloudFront leva alguns minutos para ficar
disponível. Variáveis (`name`, `region`, `schedule_expression`, `schedule_timezone`,
`log_retention_days`, `permissions_boundary`) têm padrão em `variables.tf`; mude com `-var` ou um
`terraform.tfvars`.

Se a sua conta exige um permissions boundary nos papéis criados, passe o ARN:
`tofu apply -var permissions_boundary=arn:aws:iam::<conta>:policy/<boundary>`. Os nomes começam
com `name` (bucket `journal-site-*`, função `journal-build`) e os papéis levam a tag
`Project = name`, o que permite um boundary por tag.

O estado fica em `deploy/terraform.tfstate` (fora do git). Para guardar no S3, copie
`backend.tf.example` para `backend.tf`, ajuste o bucket e rode `tofu init -migrate-state`.

## Atualizar (código ou fontes)

```sh
./deploy/build.sh && (cd deploy && tofu apply)
```

O `journal.toml` vai dentro do pacote: mudou uma fonte, rode de novo.

## Rodar na hora, sem esperar as 8h

```sh
aws lambda invoke --function-name "$(cd deploy && tofu output -raw function_name)" /dev/stdout
```

Rodar de novo no mesmo dia cria uma revisão (`edicoes/AAAA-MM-DD-2/`); nada é sobrescrito.

## Logs

```sh
aws logs tail /aws/lambda/journal-build --follow
```

## Como funciona

- Na Lambda, `JOURNAL_BUCKET` faz o site ir para o bucket, no lugar do `storage` local do
  `journal.toml`. Para gravar no S3 a partir da sua máquina, use
  `storage = { type = "s3", bucket = "<BucketName>" }` e instale `journal[aws]`.
- Cache: `index.html`, `edicoes/index.html`, `editions.json` e `seen.json` com 5 minutos; as
  edições, que nunca mudam, com 1 ano.
- O bucket guarda versões antigas por 30 dias (`index.html` e manifestos também têm histórico).
- Logs ficam 14 dias.
- Falha: a Lambda tenta mais uma vez. Fontes que falham só aparecem no log; o build só falha se
  nenhuma fonte responder ou se não conseguir gravar no S3.

## Remover tudo

Esvazie o bucket (inclusive versões) e rode `cd deploy && tofu destroy`.
