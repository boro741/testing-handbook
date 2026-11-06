terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }
}

# Credentials come from your environment (profile, SSO or role), never from this code.
provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      project = var.name_prefix
      purpose = "capacity-test"
      owner   = var.owner_tag
    }
  }
}
