variable "table_name" {
  type        = string
  description = "Nombre de la tabla DynamoDB"
  default     = "sentinel_data"
}

variable "read_capacity" {
  type        = number
  description = "Capacidad de lectura provisionada"
  default     = 5
}

variable "write_capacity" {
  type        = number
  description = "Capacidad de escritura provisionada"
  default     = 5
}

variable "tag_name" {
  type        = string
  description = "Valor del tag Name"
  default     = "Sentinel-DB"
}
