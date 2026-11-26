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
- [AWS SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html)
- [uv](https://docs.astral.sh/uv/)

## Primeiro deploy

```sh
./deploy/build.sh                                # empacota em build/
sam deploy --guided --template-file deploy/template.yaml
```

No `--guided`: escolha um nome de stack (ex.: `journal`), a região (ex.: `sa-east-1`), aceite
criar o papel IAM e salve as respostas em `samconfig.toml`. No fim, `SiteUrl` é o endereço do
jornal. O CloudFront leva alguns minutos para ficar disponível.

## Atualizar (código ou fontes)

```sh
./deploy/build.sh && sam deploy --template-file deploy/template.yaml
```

O `journal.toml` vai dentro do pacote: mudou uma fonte, rode de novo.

## Rodar na hora, sem esperar as 8h

```sh
aws lambda invoke --function-name <FunctionName> /dev/stdout
```

Rodar de novo no mesmo dia cria uma revisão (`edicoes/AAAA-MM-DD-2/`); nada é sobrescrito.

## Logs

```sh
sam logs --stack-name journal --tail
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

Esvazie o bucket (inclusive versões) e rode `sam delete --stack-name journal`.
