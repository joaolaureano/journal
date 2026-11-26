output "site_url" {
  description = "Endereço do jornal."
  value       = "https://${aws_cloudfront_distribution.site.domain_name}"
}

output "bucket_name" {
  value = aws_s3_bucket.site.id
}

output "function_name" {
  description = "Para rodar na hora (veja deploy/README.md)."
  value       = aws_lambda_function.build.function_name
}

output "deploy_role_arn" {
  description = "Vai na variável AWS_DEPLOY_ROLE_ARN do repositório."
  value       = one(aws_iam_role.ci[*].arn)
}
