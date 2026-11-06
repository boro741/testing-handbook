# TaskFlow ECS test environment (Terraform)

Describes the environment for the `task-service` capacity test as code, so the test can be repeated.

> **Status: validated with `terraform validate` (Terraform 1.9.8, AWS provider 6.72.0) using the
> `hashicorp/terraform:1.9` image on 2026-11-06. Never planned or applied.**
> The check ran with no AWS credentials and made no AWS API calls. `terraform fmt -check -recursive` also passed.

## What it creates

| File | Contents |
|---|---|
| `versions.tf` | Terraform and AWS provider versions, provider block with default tags |
| `variables.tf` | All inputs, with SLO-based alarm thresholds |
| `main.tf` | ECS cluster (Container Insights on), log group, execution role, Fargate task definition, service |
| `alb.tf` | Application Load Balancer, target group (`ip` targets), HTTP listener, security group |
| `autoscaling.tf` | Application Auto Scaling target and CPU target tracking, only when `enable_autoscaling = true` |
| `monitoring.tf` | Five CloudWatch alarms and one dashboard |
| `outputs.tf` | ALB DNS name, cluster, service, dashboard and alarm names |

It does not create a VPC, a database, secrets or an HTTPS certificate. No account id is hard-coded and no
credentials are in the code.

## Defaults worth knowing

- `enable_autoscaling` is `false` and `desired_count` is `1`, so the per-task capacity test runs one task with scaling off.
- `task_cpu = 1024` and `task_memory = 2048` is a valid Fargate pair.
- The p95 alarm threshold is `slo_p95_ms / 1000` (the metric is in seconds). The 5XX alarm threshold is
  `ceil(slo_error_rate_percent / 100 * expected_requests_per_minute)`, at least 1.
- `lifecycle.ignore_changes = [desired_count]` on the service lets auto scaling own the count. Change the count
  after creation with the console or CLI, or remove that line.
- The listener is plain HTTP on port 80, for a short-lived staging test only. `allowed_ingress_cidrs` has no default.

## How to use it (only in an account you own, with approval)

```bash
# create terraform.tfvars yourself, using the placeholders below
terraform init
terraform validate
terraform plan
```

Placeholders for `terraform.tfvars` (replace every value):

```hcl
owner_tag             = "your-team"
vpc_id                = "vpc-REPLACE_ME"
alb_subnet_ids        = ["subnet-REPLACE_A", "subnet-REPLACE_B"]
task_subnet_ids       = ["subnet-REPLACE_C", "subnet-REPLACE_D"]
allowed_ingress_cidrs = ["REPLACE_WITH_LOAD_GENERATOR_CIDR"]
container_image       = "REPLACE_WITH_IMAGE_URL:TAG"
```

Running `plan` or `apply` needs AWS credentials and creates billable resources. The handbook never did this.
Destroy the environment after the test (`terraform destroy`).

## Checks that were run here

- `terraform init -backend=false`, `terraform validate` and `terraform fmt -check -recursive` all passed on
  2026-11-06 with `hashicorp/terraform:1.9` (Terraform 1.9.8) and the AWS provider 6.72.0 from `.terraform.lock.hcl`.