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
`log_retention_days`, `permissions_boundary`, `github_subject_prefix`) têm padrão em `variables.tf`; mude com `-var` ou um
`terraform.tfvars`.

Se a sua conta exige um permissions boundary nos papéis criados, passe o ARN:
`tofu apply -var permissions_boundary=arn:aws:iam::<conta>:policy/<boundary>`. Os nomes começam
com `name` (bucket `journal-site-*`, função `journal-build`) e os papéis levam a tag
`Project = name`, o que permite um boundary por tag.

O estado fica em `deploy/terraform.tfstate` (fora do git), só na sua máquina. Para guardar no
S3, crie um bucket privado com versionamento, copie `backend.tf.example` para `backend.tf`
(também fora do git), ajuste o bucket e rode `tofu init -migrate-state`.

O provider da AWS do OpenTofu não lê perfis do `aws login`; exporte a sessão antes:
`eval "$(aws configure export-credentials --profile <perfil> --format env)"`.

## Atualizar (código ou fontes)

Com o CI ligado (abaixo), basta dar push na `main`: o GitHub Actions roda os testes e publica o
código e o `journal.toml` na função. Sem CI, ou quando mudar a infraestrutura (`deploy/*.tf`):

```sh
./deploy/build.sh && (cd deploy && tofu apply)
```

## Publicar pelo GitHub Actions

O workflow `.github/workflows/ci.yml` roda `ruff` e `pytest` em todo push e pull request. Num
push na `main`, se a variável `AWS_DEPLOY_ROLE_ARN` existir no repositório, ele empacota e
troca o código da função, assumindo um papel por OIDC (sem chave guardada). Para ligar:

1. O provedor OIDC do GitHub (`token.actions.githubusercontent.com`) precisa existir na conta.
2. `tofu apply -var github_subject_prefix=repo:<dono>/<repo>` cria o papel `journal-deploy-ci`,
   que só confia no ambiente `production` do repositório e só troca e lê o código da função.
   Se o repositório usa o formato de `sub` com IDs, passe esse prefixo.
3. No GitHub, crie o ambiente `production` (só a `main`) e a variável `AWS_DEPLOY_ROLE_ARN` com
   a saída `deploy_role_arn`. Opcionais: `AWS_REGION` e `JOURNAL_FUNCTION`.

O CI não muda infraestrutura; isso continua sendo `tofu apply`. Depois de uma publicação pelo CI,
o próximo `tofu apply` local sobe o pacote local de novo, que é o mesmo se estiver em dia.

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
