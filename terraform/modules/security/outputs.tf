output "security_group_id" {
  value       = aws_security_group.this.id
  description = "ID del Security Group de Sentinel"
}
