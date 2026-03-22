terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {}

module "security" {
  source = "./modules/security"
}

module "database" {
  source = "./modules/database"
}

module "iam" {
  source             = "./modules/iam"
  dynamodb_table_arn = module.database.table_arn
}

module "compute" {
  source                    = "./modules/compute"
  iam_instance_profile_name = module.iam.instance_profile_name
  security_group_id         = module.security.security_group_id
  public_key_content        = file("~/.ssh/sentinel_key.pub")
}

output "ip_publica" {
  value       = module.compute.public_ip
  description = "La IP publica para conectarte por SSH"
}