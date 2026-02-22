terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {}

data "aws_ami" "al2023" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["al2023-ami-2023.*-x86_64"]
  }

  filter {
    name   = "architecture"
    values = ["x86_64"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

resource "aws_key_pair" "sentinel_key" {
  key_name   = "sentinel_key"
  public_key = file("~/.ssh/sentinel_key.pub")
}

resource "aws_security_group" "sentinel_sg" {
  name        = "sentinel_sg"
  description = "Permitir SSH y HTTP"

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_instance" "sentinel_server" {
  ami           = data.aws_ami.al2023.id 
  instance_type = "t3.micro" 

  vpc_security_group_ids = [aws_security_group.sentinel_sg.id]
  key_name               = aws_key_pair.sentinel_key.key_name

  tags = {
    Name = "Sentinel-AL2023-Server"
  }

  user_data = <<-EOF
              #!/bin/bash
              # 1. Actualizar el sistema
              dnf update -y
              
              # 2. Instalar Nginx, Git y Docker
              dnf install -y nginx git docker
              
              # 3. Encender Nginx y Docker de inmediato y configurarlos para que arranquen si la máquina se reinicia
              systemctl enable --now nginx
              systemctl enable --now docker
              
              # 4. Darle permisos a tu usuario (ec2-user) para usar contenedores sin necesidad de escribir 'sudo'
              usermod -aG docker ec2-user
              EOF
}

output "ip_publica" {
  value       = aws_instance.sentinel_server.public_ip
  description = "La IP publica para conectarte por SSH"
}