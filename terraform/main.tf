terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.0"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "~> 2.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# VPC and Networking
module "vpc" {
  source = "./modules/vpc"
  
  vpc_name = var.vpc_name
  vpc_cidr = var.vpc_cidr
  azs      = var.availability_zones
}

# EKS Cluster
module "eks" {
  source = "./modules/eks"
  
  cluster_name    = var.cluster_name
  cluster_version = var.cluster_version
  vpc_id          = module.vpc.vpc_id
  subnet_ids      = module.vpc.private_subnets
  
  node_groups = {
    general = {
      desired_capacity = 2
      max_capacity     = 4
      min_capacity     = 1
      instance_types   = ["t3.medium"]
    }
    gpu = {
      desired_capacity = 1
      max_capacity     = 3
      min_capacity     = 0
      instance_types   = ["g4dn.xlarge"]
      labels = {
        "node.kubernetes.io/gpu" = "true"
      }
    }
  }
}

# RDS PostgreSQL
module "rds" {
  source = "./modules/rds"
  
  cluster_name = var.cluster_name
  vpc_id       = module.vpc.vpc_id
  subnet_ids   = module.vpc.private_subnets
  
  db_name     = var.db_name
  db_username = var.db_username
  db_password = var.db_password
}

# ElastiCache Redis
module "redis" {
  source = "./modules/redis"
  
  cluster_name = var.cluster_name
  vpc_id       = module.vpc.vpc_id
  subnet_ids   = module.vpc.private_subnets
}

# S3 Bucket for images
module "s3" {
  source = "./modules/s3"
  
  bucket_name = var.s3_bucket_name
}

# Secrets Manager
module "secrets" {
  source = "./modules/secrets"
  
  cluster_name = var.cluster_name
  db_password  = var.db_password
  jwt_secret   = var.jwt_secret
}

# Load Balancer Controller
module "lb_controller" {
  source = "./modules/lb-controller"
  
  cluster_name = var.cluster_name
  vpc_id       = module.vpc.vpc_id
}

# External DNS
module "external_dns" {
  source = "./modules/external-dns"
  
  cluster_name = var.cluster_name
  domain_name  = var.domain_name
}

# Cert Manager
module "cert_manager" {
  source = "./modules/cert-manager"
  
  cluster_name = var.cluster_name
  email        = var.cert_email
}
