variable "name" {
  description = "Prefixo dos recursos (bucket, função, agendamento)."
  type        = string
  default     = "journal"
}

variable "region" {
  description = "Região da AWS."
  type        = string
  default     = "us-east-1"
}

variable "schedule_expression" {
  description = "Quando gerar a edição (sintaxe do EventBridge Scheduler)."
  type        = string
  default     = "cron(0 8 * * ? *)"
}

variable "schedule_timezone" {
  description = "Fuso do agendamento; deve bater com o timezone do journal.toml."
  type        = string
  default     = "America/Sao_Paulo"
}

variable "log_retention_days" {
  description = "Por quantos dias guardar os logs da Lambda."
  type        = number
  default     = 14
}

variable "permissions_boundary" {
  description = "ARN de um permissions boundary para os papéis criados (opcional)."
  type        = string
  default     = null
}
