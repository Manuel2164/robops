terraform {
  required_providers {
    aws = { source = "hashicorp/aws", version = "~> 5.0" }
  }
}

provider "aws" { region = "us-east-1" }

# IoT Thing Group — robot fleet
resource "aws_iot_thing_group" "robot_fleet" {
  name = "robops-fleet"
}

# 3 simulated robots as IoT Things
resource "aws_iot_thing" "robot" {
  count = 3
  name  = "robot-${count.index + 1}"
}

resource "aws_iot_thing_group_membership" "membership" {
  count            = 3
  thing_name       = aws_iot_thing.robot[count.index].name
  thing_group_name = aws_iot_thing_group.robot_fleet.name
}

# IoT Policy
resource "aws_iot_policy" "robot_policy" {
  name = "robops-policy"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = ["iot:Connect", "iot:Publish", "iot:Subscribe", "iot:Receive"]
      Resource = "*"
    }]
  })
}

# S3 bucket for artifacts
resource "aws_s3_bucket" "artifacts" {
  bucket        = "robops-artifacts-my-robops-2335"
  force_destroy = true
}

# ECR repository
resource "aws_ecr_repository" "robot_app" {
  name                 = "robot-app"
  image_tag_mutability = "MUTABLE"
}

output "ecr_url"        { value = aws_ecr_repository.robot_app.repository_url }
output "s3_bucket_name" { value = aws_s3_bucket.artifacts.bucket }
