# Target tracking on average CPU. Off by default so the one-task capacity test is not disturbed.

resource "aws_appautoscaling_target" "task_service" {
  count = var.enable_autoscaling ? 1 : 0

  min_capacity       = var.autoscaling_min_tasks
  max_capacity       = var.autoscaling_max_tasks
  resource_id        = "service/${aws_ecs_cluster.this.name}/${aws_ecs_service.task_service.name}"
  scalable_dimension = "ecs:service:DesiredCount"
  service_namespace  = "ecs"
}

resource "aws_appautoscaling_policy" "cpu" {
  count = var.enable_autoscaling ? 1 : 0

  name               = "${var.name_prefix}-cpu-target-tracking"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.task_service[0].resource_id
  scalable_dimension = aws_appautoscaling_target.task_service[0].scalable_dimension
  service_namespace  = aws_appautoscaling_target.task_service[0].service_namespace

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageCPUUtilization"
    }

    target_value       = var.autoscaling_cpu_target_percent
    scale_out_cooldown = 300
    scale_in_cooldown  = 300
  }
}
