# Papel que o GitHub Actions assume por OIDC para publicar o código da função:
# sem chave guardada, só o ambiente production do repositório e só trocar e ler
# o código. Infraestrutura continua sendo tofu apply local.
# Criado só com github_subject_prefix; o provedor OIDC do GitHub já precisa
# existir na conta.

data "aws_iam_openid_connect_provider" "github" {
  count = var.github_subject_prefix == null ? 0 : 1
  url   = "https://token.actions.githubusercontent.com"
}

data "aws_iam_policy_document" "ci_trust" {
  count = var.github_subject_prefix == null ? 0 : 1

  statement {
    actions = ["sts:AssumeRoleWithWebIdentity"]
    principals {
      type        = "Federated"
      identifiers = [data.aws_iam_openid_connect_provider.github[0].arn]
    }
    condition {
      test     = "StringEquals"
      variable = "token.actions.githubusercontent.com:aud"
      values   = ["sts.amazonaws.com"]
    }
    condition {
      test     = "StringEquals"
      variable = "token.actions.githubusercontent.com:sub"
      values   = ["${var.github_subject_prefix}:environment:production"]
    }
  }
}

resource "aws_iam_role" "ci" {
  count                = var.github_subject_prefix == null ? 0 : 1
  name                 = "${var.name}-deploy-ci"
  assume_role_policy   = data.aws_iam_policy_document.ci_trust[0].json
  permissions_boundary = var.permissions_boundary
}

data "aws_iam_policy_document" "ci" {
  statement {
    actions = [
      "lambda:UpdateFunctionCode",
      "lambda:GetFunction",
      "lambda:GetFunctionConfiguration",
    ]
    resources = [aws_lambda_function.build.arn]
  }
}

resource "aws_iam_role_policy" "ci" {
  count  = var.github_subject_prefix == null ? 0 : 1
  role   = aws_iam_role.ci[0].id
  policy = data.aws_iam_policy_document.ci.json
}
