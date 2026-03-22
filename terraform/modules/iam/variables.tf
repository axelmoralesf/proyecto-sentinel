variable "role_name" {
  type        = string
  description = "Nombre del rol IAM"
  default     = "ec2_dynamo_role"
}

variable "policy_name" {
  type        = string
  description = "Nombre de la policy inline IAM"
  default     = "dynamo_access_policy"
}

variable "instance_profile_name" {
  type        = string
  description = "Nombre del instance profile para EC2"
  default     = "ec2_dynamo_profile"
}

variable "dynamodb_table_arn" {
  type        = string
  description = "ARN de la tabla DynamoDB"
}
