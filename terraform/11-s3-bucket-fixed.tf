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

# FIX 11 — S3 Bucket Private (sécurisé)
resource "aws_s3_bucket" "app_data" {
  bucket = "myapp-data-bucket-${data.aws_caller_identity.current.account_id}"
}

# ✓ SÉCURISÉ : bloque tout accès public
resource "aws_s3_bucket_public_access_block" "app_data" {
  bucket = aws_s3_bucket.app_data.id

  block_public_acls       = true   # ← Bloque les ACLs publiques
  block_public_policy     = true   # ← Bloque les policies publiques
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# ✓ SÉCURISÉ : pas de policy publique
# L'accès se fait via IAM roles seulement
resource "aws_s3_bucket_policy" "app_data" {
  bucket = aws_s3_bucket.app_data.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "AllowAppRole"
        Effect = "Allow"
        Principal = {
          AWS = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/app-role"
        }
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

# ✓ SÉCURISÉ : fichier privé (pas d'ACL public)
resource "aws_s3_object" "backup" {
  bucket = aws_s3_bucket.app_data.id
  key    = "backup-2024.sql"
  source = "/tmp/backup-2024.sql"
  # ← Pas de "acl = public-read" (default = private)
}

# Activer versioning pour audit trail
resource "aws_s3_bucket_versioning" "app_data" {
  bucket = aws_s3_bucket.app_data.id
  versioning_configuration {
    status = "Enabled"
  }
}

# Activer server-side encryption
resource "aws_s3_bucket_server_side_encryption_configuration" "app_data" {
  bucket = aws_s3_bucket.app_data.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# Activer logging pour audit
resource "aws_s3_bucket_logging" "app_data" {
  bucket = aws_s3_bucket.app_data.id

  target_bucket = aws_s3_bucket.logs.id
  target_prefix = "app-data-logs/"
}

resource "aws_s3_bucket" "logs" {
  bucket = "myapp-logs-bucket-${data.aws_caller_identity.current.account_id}"
}

resource "aws_s3_bucket_public_access_block" "logs" {
  bucket = aws_s3_bucket.logs.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

data "aws_caller_identity" "current" {}
