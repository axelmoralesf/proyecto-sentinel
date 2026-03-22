output "public_ip" {
  value       = aws_eip.sentinel_eip.public_ip
  description = "IP publica de la instancia Sentinel"
}
