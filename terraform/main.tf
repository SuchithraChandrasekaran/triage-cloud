terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "us-east-1"
}

resource "aws_s3_bucket" "triage_cloud_test" {
  bucket = "triage-cloud-test-bucket-suchithra"

  tags = {
    Project = "triage-cloud"
  }
}
