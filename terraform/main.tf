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
              # 1. Actualizar el sistema e instalar dependencias base
              dnf update -y
              dnf install -y nginx git docker
              
              # 2. Instalar docker-compose globalmente en /usr/bin (a prueba de non-interactive shells)
              curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-linux-$(uname -m)" -o /usr/bin/docker-compose
              chmod +x /usr/bin/docker-compose
              
              # 3. Encender Nginx y Docker de inmediato y configurarlos para arranque automático
              systemctl enable --now nginx
              systemctl enable --now docker
              
              # 4. Darle permisos al usuario para usar contenedores sin 'sudo'
              usermod -aG docker ec2-user
              EOF
}

resource "aws_eip" "sentinel_eip" {
  instance = aws_instance.sentinel_server.id
  domain = "vpc"
}

output "ip_publica" {
  value       = aws_eip.sentinel_eip.public_ip
  description = "La IP publica para conectarte por SSH"
}