variable "iam_instance_profile_name" {
  type        = string
  description = "Nombre del IAM Instance Profile"
}

variable "security_group_id" {
  type        = string
  description = "Security Group ID asignado a la instancia"
}

variable "key_name" {
  type        = string
  description = "Nombre del key pair"
  default     = "sentinel_key"
}

variable "public_key_content" {
  type        = string
  description = "Contenido de la llave publica SSH"
}

variable "instance_type" {
  type        = string
  description = "Tipo de instancia EC2"
  default     = "t3.micro"
}

variable "ami_name_pattern" {
  type        = string
  description = "Patron de nombre para la AMI"
  default     = "al2023-ami-2023.*-x86_64"
}

variable "instance_tag_name" {
  type        = string
  description = "Valor del tag Name para la instancia"
  default     = "Sentinel-AL2023-Server"
}
