# AI Kiosk — central infrastructure (light skeleton).
#
# Production central: Postgres 17 + pgvector (system of record), S3-compatible
# object storage (media + signed bundles), an on-demand GPU node for fine-tuning
# (Unsloth/axolotl + PEFT/LoRA), and a K3s cluster for stateless services.
# Placeholders only — replace with the organisation's managed-offering standard.
terraform {
  required_version = ">= 1.6"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

variable "region" {
  default = "ap-south-1"
}

provider "aws" {
  region = var.region
}

# ── System of record: Postgres 17 + pgvector ────────────────────────────────
# The canonical case graph (S7) lives here. Production: HA, encryption-at-rest,
# automated backups + PITR. Replace with a managed offering that ships pgvector.
resource "aws_db_instance" "system_of_record" {
  identifier     = "ai-kiosk-postgres"
  engine         = "postgres"
  engine_version = "17"
  instance_class = "db.t4g.medium"
  allocated_storage   = 100
  multi_az            = true
  storage_encrypted   = true
  backup_retention_period = 30
  # NB: enable the pgvector extension once the cluster is up (0001 migration).
}

# ── Object storage: media + signed bundles ───────────────────────────────────
resource "aws_s3_bucket" "media" {
  bucket = "ai-kiosk-media-prod"
}

resource "aws_s3_bucket" "bundles" {
  bucket = "ai-kiosk-bundles-prod"
}

# ── GPU node (on-demand) for fine-tuning — S26 ───────────────────────────────
# Ephemeral; used by mlops-service for LoRA fine-tuning and eval-gate runs.
# resource "aws_instance" "gpu_node" { ... }

# ── Keycloak realm import is handled by infra/keycloak/ai-kiosk-realm.json ────
