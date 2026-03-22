resource "aws_dynamodb_table" "this" {
  name           = var.table_name
  billing_mode   = "PROVISIONED"
  read_capacity  = var.read_capacity
  write_capacity = var.write_capacity
  hash_key       = "agent_id"
  range_key      = "timestamp"

  attribute {
    name = "agent_id"
    type = "S" #String
  }

  attribute {
    name = "timestamp"
    type = "S" #String
  }

  tags = {
    Name = var.tag_name
  }
}
