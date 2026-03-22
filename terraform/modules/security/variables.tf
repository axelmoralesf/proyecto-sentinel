variable "name" {
  type        = string
  description = "Nombre del Security Group"
  default     = "sentinel_sg"
}

variable "description" {
  type        = string
  description = "Descripcion del Security Group"
  default     = "Permitir SSH y HTTP"
}

variable "ssh_cidr" {
  type        = string
  description = "CIDR permitido para SSH"
  default     = "0.0.0.0/0"
}

variable "http_cidr" {
  type        = string
  description = "CIDR permitido para HTTP"
  default     = "0.0.0.0/0"
}
