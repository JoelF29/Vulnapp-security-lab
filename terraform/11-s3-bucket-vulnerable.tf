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

# FAILLE 11 — S3 Bucket Public (vulnérable)
resource "aws_s3_bucket" "app_data" {
  bucket = "myapp-data-bucket-${data.aws_caller_identity.current.account_id}"
}

# ❌ VULNÉRABLE : rend le bucket public
resource "aws_s3_bucket_public_access_block" "app_data" {
  bucket = aws_s3_bucket.app_data.id

  block_public_acls       = false  # ← Permet les ACLs publiques
  block_public_policy     = false  # ← Permet les policies publiques
  ignore_public_acls      = false
  restrict_public_buckets = false
}

# ❌ VULNÉRABLE : policy publique
resource "aws_s3_bucket_policy" "app_data" {
  bucket = aws_s3_bucket.app_data.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "PublicRead"
        Effect = "Allow"
        Principal = "*"  # ← N'importe qui sur internet
        Action = [
          "s3:GetObject",
          "s3:ListBucket"
        ]
        Resource = [
          aws_s3_bucket.app_data.arn,
          "${aws_s3_bucket.app_data.arn}/*"
        ]
      }
    ]
  })
}

# Fichier sensible — normalement ne devrait PAS être public
resource "aws_s3_object" "backup" {
  bucket = aws_s3_bucket.app_data.id
  key    = "backup-2024.sql"
  source = "/tmp/backup-2024.sql"  # Base de données complète
  acl    = "public-read"  # ← Fichier public
}

data "aws_caller_identity" "current" {}
