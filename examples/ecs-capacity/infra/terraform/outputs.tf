output "alb_dns_name" {
  description = "Point the load generator at this host name."
  value       = aws_lb.this.dns_name
}

output "cluster_name" {
  description = "ECS cluster name, for CloudWatch queries."
  value       = aws_ecs_cluster.this.name
}

output "service_name" {
  description = "ECS service name, for CloudWatch queries."
  value       = aws_ecs_service.task_service.name
}

output "dashboard_name" {
  description = "CloudWatch dashboard name."
  value       = aws_cloudwatch_dashboard.capacity.dashboard_name
}

output "alarm_names" {
  description = "Names of the CloudWatch alarms."
  value = [
    aws_cloudwatch_metric_alarm.p95_latency.alarm_name,
    aws_cloudwatch_metric_alarm.target_5xx.alarm_name,
    aws_cloudwatch_metric_alarm.unhealthy_hosts.alarm_name,
    aws_cloudwatch_metric_alarm.ecs_cpu.alarm_name,
    aws_cloudwatch_metric_alarm.ecs_memory.alarm_name,
  ]
}

output "autoscaling_enabled" {
  description = "Whether the CPU target tracking policy exists."
  value       = var.enable_autoscaling
}
