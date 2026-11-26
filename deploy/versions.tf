terraform {
  required_version = ">= 1.6"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.40"
    }
    archive = {
      source  = "hashicorp/archive"
      version = ">= 2.4"
    }
  }

  # Estado local por padrão. Para guardar no S3, veja backend.tf.example.
}

provider "aws" {
  region = var.region

  default_tags {
    tags = { Project = var.name }
  }
}
