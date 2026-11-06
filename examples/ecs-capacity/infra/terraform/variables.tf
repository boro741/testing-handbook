# ---------- Where it runs ----------
variable "aws_region" {
  description = "Region for every resource. Keep the load generator in the same region."
  type        = string
  default     = "eu-west-1"
}

variable "name_prefix" {
  description = "Prefix for resource names, for example taskflow-staging."
  type        = string
  default     = "taskflow-staging"
}

variable "owner_tag" {
  description = "Who owns this test environment. Used as a tag so it can be found and removed."
  type        = string
}

variable "vpc_id" {
  description = "Existing VPC id. This code does not create a VPC."
  type        = string
}

variable "alb_subnet_ids" {
  description = "Subnet ids for the load balancer (at least two, in different Availability Zones)."
  type        = list(string)
}

variable "task_subnet_ids" {
  description = "Subnet ids for the Fargate tasks."
  type        = list(string)
}

variable "assign_public_ip" {
  description = "Give tasks a public IP. Needed only when task subnets have no NAT or image endpoints."
  type        = bool
  default     = false
}

variable "allowed_ingress_cidrs" {
  description = "CIDR blocks allowed to reach the ALB, for example the load generator. No default on purpose."
  type        = list(string)
}

# ---------- The task ----------
variable "container_image" {
  description = "Container image for task-service, for example a registry URL with a tag."
  type        = string
}

variable "container_port" {
  description = "Port the container listens on."
  type        = number
  default     = 8000
}

variable "health_check_path" {
  description = "Path the ALB calls to check a task. TaskFlow exposes /health."
  type        = string
  default     = "/health"
}

variable "task_cpu" {
  description = "Fargate CPU units. Must pair with task_memory from the valid Fargate table."
  type        = number
  default     = 1024

  validation {
    condition     = contains([256, 512, 1024, 2048, 4096, 8192, 16384], var.task_cpu)
    error_message = "task_cpu must be one of 256, 512, 1024, 2048, 4096, 8192, 16384."
  }
}

variable "task_memory" {
  description = "Fargate memory in MiB. 1024 CPU pairs with 2048 to 8192."
  type        = number
  default     = 2048
}

variable "desired_count" {
  description = "Initial task count. Keep 1 for the per-task capacity test."
  type        = number
  default     = 1
}

variable "log_retention_days" {
  description = "How long to keep task logs."
  type        = number
  default     = 7
}

# ---------- Auto scaling ----------
variable "enable_autoscaling" {
  description = "Create the Application Auto Scaling target and CPU policy. Keep false for the one-task capacity test."
  type        = bool
  default     = false
}

variable "autoscaling_min_tasks" {
  description = "Lowest task count when auto scaling is on."
  type        = number
  default     = 2
}

variable "autoscaling_max_tasks" {
  description = "Highest task count when auto scaling is on."
  type        = number
  default     = 6
}

variable "autoscaling_cpu_target_percent" {
  description = "Target for average service CPU utilisation, in percent."
  type        = number
  default     = 60
}

# ---------- SLO and alarm thresholds ----------
variable "slo_p95_ms" {
  description = "SLO: p95 response time in milliseconds. The latency alarm uses this value."
  type        = number
  default     = 300
}

variable "slo_error_rate_percent" {
  description = "SLO: allowed share of failed requests, in percent."
  type        = number
  default     = 1
}

variable "expected_requests_per_minute" {
  description = "Planned request volume per minute. With the SLO error rate, it sets the 5XX count threshold."
  type        = number
  default     = 9000
}

variable "cpu_alarm_percent" {
  description = "Alarm when service CPU utilisation (average) passes this percent."
  type        = number
  default     = 80
}

variable "memory_alarm_percent" {
  description = "Alarm when service memory utilisation (average) passes this percent."
  type        = number
  default     = 80
}

variable "alarm_evaluation_periods" {
  description = "Consecutive 60-second periods that must breach before an alarm fires."
  type        = number
  default     = 3
}

variable "alarm_sns_topic_arns" {
  description = "SNS topic ARNs to notify. Empty means alarms change state but notify nobody."
  type        = list(string)
  default     = []
}
