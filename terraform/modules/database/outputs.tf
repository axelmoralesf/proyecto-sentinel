output "table_arn" {
  value       = aws_dynamodb_table.this.arn
  description = "ARN de la tabla DynamoDB"
}
