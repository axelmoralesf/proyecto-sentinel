output "instance_profile_name" {
  value       = aws_iam_instance_profile.ec2_profile.name
  description = "Nombre del Instance Profile para EC2"
}
