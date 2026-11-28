# Uma edição estática por dia: o Scheduler chama a Lambda, que gera o site e grava
# num bucket S3 privado; o CloudFront serve o bucket.

locals {
  build_dir = "${path.module}/../build"
}

# --- Site: bucket privado, versionado, servido só pelo CloudFront ---

resource "aws_s3_bucket" "site" {
  bucket_prefix = "${var.name}-site-"
}

resource "aws_s3_bucket_versioning" "site" {
  bucket = aws_s3_bucket.site.id
  versioning_configuration {
    status = "Enabled" # histórico também de index.html, editions.json e seen.json
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "site" {
  bucket     = aws_s3_bucket.site.id
  depends_on = [aws_s3_bucket_versioning.site]

  rule {
    id     = "expire-old-versions"
    status = "Enabled"
    filter {}
    noncurrent_version_expiration {
      noncurrent_days = 30
    }
  }

  # o coletor regrava cada arquivo do pool de hora em hora; versões antigas não servem
  rule {
    id     = "expire-old-pool-versions"
    status = "Enabled"
    filter {
      prefix = "pool/"
    }
    noncurrent_version_expiration {
      noncurrent_days = 1
    }
  }
}

resource "aws_s3_bucket_public_access_block" "site" {
  bucket                  = aws_s3_bucket.site.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_server_side_encryption_configuration" "site" {
  bucket = aws_s3_bucket.site.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_cloudfront_origin_access_control" "site" {
  name                              = "${var.name}-site"
  origin_access_control_origin_type = "s3"
  signing_behavior                  = "always"
  signing_protocol                  = "sigv4"
}

# Respeita o Cache-Control que o journal grava: 5 min para index.html e
# manifestos, 1 ano para as edições, que nunca mudam.
data "aws_cloudfront_cache_policy" "optimized" {
  name = "Managed-CachingOptimized"
}

resource "aws_cloudfront_distribution" "site" {
  enabled             = true
  comment             = "${var.name} journal"
  default_root_object = "index.html"
  http_version        = "http2and3"

  origin {
    origin_id                = "site"
    domain_name              = aws_s3_bucket.site.bucket_regional_domain_name
    origin_access_control_id = aws_cloudfront_origin_access_control.site.id
  }

  default_cache_behavior {
    target_origin_id       = "site"
    viewer_protocol_policy = "redirect-to-https"
    allowed_methods        = ["GET", "HEAD"]
    cached_methods         = ["GET", "HEAD"]
    compress               = true
    cache_policy_id        = data.aws_cloudfront_cache_policy.optimized.id
  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  viewer_certificate {
    cloudfront_default_certificate = true
  }
}

data "aws_iam_policy_document" "cloudfront_reads_site" {
  statement {
    actions   = ["s3:GetObject"]
    resources = ["${aws_s3_bucket.site.arn}/*"]
    principals {
      type        = "Service"
      identifiers = ["cloudfront.amazonaws.com"]
    }
    condition {
      test     = "StringEquals"
      variable = "AWS:SourceArn"
      values   = [aws_cloudfront_distribution.site.arn]
    }
  }
}

resource "aws_s3_bucket_policy" "site" {
  bucket     = aws_s3_bucket.site.id
  policy     = data.aws_iam_policy_document.cloudfront_reads_site.json
  depends_on = [aws_s3_bucket_public_access_block.site]
}

# --- Lambda que gera a edição ---

data "archive_file" "build" {
  type        = "zip"
  source_dir  = local.build_dir
  output_path = "${path.module}/build.zip"
}

data "aws_iam_policy_document" "lambda_assume" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "build" {
  name_prefix          = "${var.name}-build-"
  assume_role_policy   = data.aws_iam_policy_document.lambda_assume.json
  permissions_boundary = var.permissions_boundary
}

data "aws_caller_identity" "current" {}

data "aws_iam_policy_document" "build" {
  statement {
    sid       = "WriteSite"
    actions   = ["s3:GetObject", "s3:PutObject"]
    resources = ["${aws_s3_bucket.site.arn}/*"]
  }
  statement {
    # Sem ListBucket, um objeto inexistente responde 403 em vez de 404.
    sid       = "ListSite"
    actions   = ["s3:ListBucket"]
    resources = [aws_s3_bucket.site.arn]
  }
  statement {
    # Chave da DeepSeek (SecureString criado à mão; nunca no repositório).
    sid       = "ReadSummarizerKey"
    actions   = ["ssm:GetParameter"]
    resources = ["arn:aws:ssm:${var.region}:${data.aws_caller_identity.current.account_id}:parameter/${var.name}/deepseek-api-key"]
  }
  statement {
    sid       = "Logs"
    actions   = ["logs:CreateLogStream", "logs:PutLogEvents"]
    resources = ["${aws_cloudwatch_log_group.build.arn}:*"]
  }
}

resource "aws_iam_role_policy" "build" {
  role   = aws_iam_role.build.id
  policy = data.aws_iam_policy_document.build.json
}

resource "aws_cloudwatch_log_group" "build" {
  name              = "/aws/lambda/${var.name}-build"
  retention_in_days = var.log_retention_days
}

resource "aws_lambda_function" "build" {
  function_name    = "${var.name}-build"
  description      = "Gera a edição do dia e publica no bucket do site."
  role             = aws_iam_role.build.arn
  handler          = "journal.aws_lambda.handler"
  runtime          = "python3.12"
  architectures    = ["arm64"]
  memory_size      = 256
  timeout          = 600
  filename         = data.archive_file.build.output_path
  source_code_hash = data.archive_file.build.output_base64sha256

  environment {
    variables = {
      JOURNAL_BUCKET                 = aws_s3_bucket.site.id
      JOURNAL_DEEPSEEK_KEY_PARAMETER = "/${var.name}/deepseek-api-key"
    }
  }

  depends_on = [aws_cloudwatch_log_group.build, aws_iam_role_policy.build]
}

resource "aws_lambda_function_event_invoke_config" "build" {
  function_name          = aws_lambda_function.build.function_name
  maximum_retry_attempts = 1 # uma nova tentativa vira, no máximo, uma revisão a mais
}

# --- Agendamento diário ---

data "aws_iam_policy_document" "scheduler_assume" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["scheduler.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "scheduler" {
  name_prefix          = "${var.name}-scheduler-"
  assume_role_policy   = data.aws_iam_policy_document.scheduler_assume.json
  permissions_boundary = var.permissions_boundary
}

data "aws_iam_policy_document" "scheduler" {
  statement {
    actions   = ["lambda:InvokeFunction"]
    resources = [aws_lambda_function.build.arn]
  }
}

resource "aws_iam_role_policy" "scheduler" {
  role   = aws_iam_role.scheduler.id
  policy = data.aws_iam_policy_document.scheduler.json
}

resource "aws_scheduler_schedule" "daily" {
  name                         = "${var.name}-daily"
  schedule_expression          = var.schedule_expression
  schedule_expression_timezone = var.schedule_timezone

  flexible_time_window {
    mode = "OFF"
  }

  target {
    arn      = aws_lambda_function.build.arn
    role_arn = aws_iam_role.scheduler.arn
  }
}

# Coleta de hora em hora: guarda no pool o que cada feed mostrou, sem publicar.
resource "aws_scheduler_schedule" "collect" {
  name                         = "${var.name}-collect"
  schedule_expression          = var.collect_schedule_expression
  schedule_expression_timezone = var.schedule_timezone

  flexible_time_window {
    mode = "OFF"
  }

  target {
    arn      = aws_lambda_function.build.arn
    role_arn = aws_iam_role.scheduler.arn
    input    = jsonencode({ action = "collect" })
  }
}
