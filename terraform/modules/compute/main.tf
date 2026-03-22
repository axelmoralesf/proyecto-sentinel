data "aws_ami" "al2023" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = [var.ami_name_pattern]
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
  key_name   = var.key_name
  public_key = var.public_key_content
}

resource "aws_instance" "sentinel_server" {
  iam_instance_profile = var.iam_instance_profile_name
  ami                  = data.aws_ami.al2023.id
  instance_type        = var.instance_type

  vpc_security_group_ids = [var.security_group_id]
  key_name               = aws_key_pair.sentinel_key.key_name

  tags = {
    Name = var.instance_tag_name
  }

  user_data = <<-EOF
              #!/bin/bash
              dnf update -y
              dnf install -y nginx git docker

              # Instalar el plugin V2 en la ruta nativa de RHEL/Amazon Linux
              mkdir -p /usr/libexec/docker/cli-plugins/
              curl -SL "https://github.com/docker/compose/releases/latest/download/docker-compose-linux-$(uname -m)" -o /usr/libexec/docker/cli-plugins/docker-compose
              chmod +x /usr/libexec/docker/cli-plugins/docker-compose

              # Instalar el motor de compilacion Buildx
              curl -SL "https://github.com/docker/buildx/releases/download/v0.17.1/buildx-v0.17.1.linux-amd64" -o /usr/libexec/docker/cli-plugins/docker-buildx
              chmod +x /usr/libexec/docker/cli-plugins/docker-buildx

              systemctl enable --now docker
              systemctl enable --now nginx
              usermod -aG docker ec2-user
              EOF
}

resource "aws_eip" "sentinel_eip" {
  instance = aws_instance.sentinel_server.id
  domain   = "vpc"
}
