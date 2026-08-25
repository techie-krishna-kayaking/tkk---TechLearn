# Infrastructure as Code: a data-lake S3 bucket with a cost-saving lifecycle
# policy + a Glue catalog database. Read the plan with `terraform plan`.
terraform {
  required_version = ">= 1.5"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  # In a team, store state remotely + lock it so applies don't clobber:
  # backend "s3" {
  #   bucket         = "acme-tfstate"
  #   key            = "data-platform/lake.tfstate"
  #   region         = "ap-south-1"
  #   dynamodb_table = "tf-locks"   # state locking
  # }
}

provider "aws" {
  region = var.region
}

variable "region" {
  type    = string
  default = "ap-south-1"
}

variable "bucket_name" {
  type    = string
  default = "acme-datalake-prod"
}

resource "aws_s3_bucket" "lake" {
  bucket = var.bucket_name
}

# Cost optimization AS CODE: transition cold data to cheaper storage, expire old.
resource "aws_s3_bucket_lifecycle_configuration" "lake" {
  bucket = aws_s3_bucket.lake.id

  rule {
    id     = "tiered-storage"
    status = "Enabled"

    transition {
      days          = 30
      storage_class = "STANDARD_IA" # infrequent access after 30 days
    }
    transition {
      days          = 90
      storage_class = "GLACIER" # archive after 90 days
    }
    expiration {
      days = 2555 # 7-year retention, then delete
    }
  }
}

# Block public access (security default you should always set).
resource "aws_s3_bucket_public_access_block" "lake" {
  bucket                  = aws_s3_bucket.lake.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# A Glue catalog database so engines (Athena/Spark) can discover tables.
resource "aws_glue_catalog_database" "analytics" {
  name = "analytics"
}

output "lake_bucket" {
  value = aws_s3_bucket.lake.bucket
}
