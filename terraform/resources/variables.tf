variable "aws_region" {
  description = "AWS region to deploy resources"
  type        = string
  default     = "eu-west-3"
}

variable "function_name" {
  description = "Name of the Lambda function (without environment suffix)"
  type        = string
  default     = "bball-app-template"
}

variable "environment" {
  description = "Deployment environment (live or nonlive)"
  type        = string
  
  validation {
    condition     = contains(["live", "nonlive"], var.environment)
    error_message = "Environment must be either 'live' or 'nonlive'."
  }
}

variable "timeout" {
  description = "Lambda function timeout in seconds"
  type        = number
  default     = 30
}

variable "memory_size" {
  description = "Lambda function memory size in MB"
  type        = number
  default     = 128
}

variable "log_retention_days" {
  description = "CloudWatch log retention in days"
  type        = number
  default     = 7
}

variable "tags" {
  description = "Tags to apply to all resources"
  type        = map(string)
  default = {
    Project   = "bball-app"
    ManagedBy = "terraform"
  }
}
