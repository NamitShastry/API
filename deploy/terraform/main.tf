# AeroIndex / FareOS — Cloud Infrastructure Specification
# AWS ECS Fargate + RDS PostgreSQL + ElastiCache Redis

terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

variable "aws_region" {
  default = "ap-south-1" # Mumbai region for low latency to Indian aviation feeds
}

resource "aws_vpc" "aeroindex_vpc" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true
  tags = {
    Name = "aeroindex-vpc"
  }
}

# ECS Cluster for FastAPI, Celery, and Next.js / Web
resource "aws_ecs_cluster" "main" {
  name = "aeroindex-cluster"
}
