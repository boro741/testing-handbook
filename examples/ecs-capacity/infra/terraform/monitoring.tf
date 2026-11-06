# CloudWatch alarms and a dashboard. Thresholds come from the SLO variables.

locals {
  lb_dim = aws_lb.this.arn_suffix
  tg_dim = aws_lb_target_group.task_service.arn_suffix

  # 5XX count allowed per minute = SLO error rate x planned requests per minute (at least 1).
  alarm_5xx_threshold = max(1, ceil(var.slo_error_rate_percent / 100 * var.expected_requests_per_minute))
}

resource "aws_cloudwatch_metric_alarm" "p95_latency" {
  alarm_name          = "${var.name_prefix}-p95-target-response-time"
  alarm_description   = "p95 TargetResponseTime is above the SLO (seconds)."
  namespace           = "AWS/ApplicationELB"
  metric_name         = "TargetResponseTime"
  extended_statistic  = "p95"
  period              = 60
  evaluation_periods  = var.alarm_evaluation_periods
  datapoints_to_alarm = var.alarm_evaluation_periods
  threshold           = var.slo_p95_ms / 1000
  comparison_operator = "GreaterThanThreshold"
  treat_missing_data  = "notBreaching"
  alarm_actions       = var.alarm_sns_topic_arns
  ok_actions          = var.alarm_sns_topic_arns

  dimensions = {
    LoadBalancer = local.lb_dim
    TargetGroup  = local.tg_dim
  }
}

resource "aws_cloudwatch_metric_alarm" "target_5xx" {
  alarm_name          = "${var.name_prefix}-target-5xx"
  alarm_description   = "Tasks return more 5XX responses per minute than the SLO error rate allows."
  namespace           = "AWS/ApplicationELB"
  metric_name         = "HTTPCode_Target_5XX_Count"
  statistic           = "Sum"
  period              = 60
  evaluation_periods  = var.alarm_evaluation_periods
  datapoints_to_alarm = var.alarm_evaluation_periods
  threshold           = local.alarm_5xx_threshold
  comparison_operator = "GreaterThanThreshold"
  treat_missing_data  = "notBreaching"
  alarm_actions       = var.alarm_sns_topic_arns
  ok_actions          = var.alarm_sns_topic_arns

  dimensions = {
    LoadBalancer = local.lb_dim
    TargetGroup  = local.tg_dim
  }
}

resource "aws_cloudwatch_metric_alarm" "unhealthy_hosts" {
  alarm_name          = "${var.name_prefix}-unhealthy-hosts"
  alarm_description   = "Every load balancer node sees at least one unhealthy target (Minimum statistic)."
  namespace           = "AWS/ApplicationELB"
  metric_name         = "UnHealthyHostCount"
  statistic           = "Minimum"
  period              = 60
  evaluation_periods  = 2
  datapoints_to_alarm = 2
  threshold           = 0
  comparison_operator = "GreaterThanThreshold"
  treat_missing_data  = "notBreaching"
  alarm_actions       = var.alarm_sns_topic_arns
  ok_actions          = var.alarm_sns_topic_arns

  dimensions = {
    LoadBalancer = local.lb_dim
    TargetGroup  = local.tg_dim
  }
}

resource "aws_cloudwatch_metric_alarm" "ecs_cpu" {
  alarm_name          = "${var.name_prefix}-ecs-cpu-utilization"
  alarm_description   = "Service CPU utilisation (percent of reserved CPU) is high."
  namespace           = "AWS/ECS"
  metric_name         = "CPUUtilization"
  statistic           = "Average"
  period              = 60
  evaluation_periods  = var.alarm_evaluation_periods
  datapoints_to_alarm = var.alarm_evaluation_periods
  threshold           = var.cpu_alarm_percent
  comparison_operator = "GreaterThanThreshold"
  treat_missing_data  = "notBreaching"
  alarm_actions       = var.alarm_sns_topic_arns
  ok_actions          = var.alarm_sns_topic_arns

  dimensions = {
    ClusterName = aws_ecs_cluster.this.name
    ServiceName = aws_ecs_service.task_service.name
  }
}

resource "aws_cloudwatch_metric_alarm" "ecs_memory" {
  alarm_name          = "${var.name_prefix}-ecs-memory-utilization"
  alarm_description   = "Service memory utilisation (percent of reserved memory) is high."
  namespace           = "AWS/ECS"
  metric_name         = "MemoryUtilization"
  statistic           = "Average"
  period              = 60
  evaluation_periods  = var.alarm_evaluation_periods
  datapoints_to_alarm = var.alarm_evaluation_periods
  threshold           = var.memory_alarm_percent
  comparison_operator = "GreaterThanThreshold"
  treat_missing_data  = "notBreaching"
  alarm_actions       = var.alarm_sns_topic_arns
  ok_actions          = var.alarm_sns_topic_arns

  dimensions = {
    ClusterName = aws_ecs_cluster.this.name
    ServiceName = aws_ecs_service.task_service.name
  }
}

resource "aws_cloudwatch_dashboard" "capacity" {
  dashboard_name = "${var.name_prefix}-capacity"

  dashboard_body = jsonencode({
    widgets = [
      {
        type = "metric", x = 0, y = 0, width = 12, height = 6
        properties = {
          title  = "TargetResponseTime p95 (seconds) vs SLO"
          region = var.aws_region
          period = 60
          metrics = [
            ["AWS/ApplicationELB", "TargetResponseTime", "LoadBalancer", local.lb_dim, "TargetGroup", local.tg_dim, { stat = "p95" }]
          ]
          annotations = {
            horizontal = [{ label = "SLO p95", value = var.slo_p95_ms / 1000 }]
          }
        }
      },
      {
        type = "metric", x = 12, y = 0, width = 12, height = 6
        properties = {
          title  = "RequestCountPerTarget and RunningTaskCount"
          region = var.aws_region
          period = 60
          metrics = [
            ["AWS/ApplicationELB", "RequestCountPerTarget", "LoadBalancer", local.lb_dim, "TargetGroup", local.tg_dim, { stat = "Sum" }],
            ["ECS/ContainerInsights", "RunningTaskCount", "ClusterName", aws_ecs_cluster.this.name, "ServiceName", aws_ecs_service.task_service.name, { stat = "Average", yAxis = "right" }]
          ]
        }
      },
      {
        type = "metric", x = 0, y = 6, width = 12, height = 6
        properties = {
          title  = "HTTPCode_Target_5XX_Count"
          region = var.aws_region
          period = 60
          metrics = [
            ["AWS/ApplicationELB", "HTTPCode_Target_5XX_Count", "LoadBalancer", local.lb_dim, "TargetGroup", local.tg_dim, { stat = "Sum" }]
          ]
          annotations = {
            horizontal = [{ label = "SLO-based limit", value = local.alarm_5xx_threshold }]
          }
        }
      },
      {
        type = "metric", x = 12, y = 6, width = 12, height = 6
        properties = {
          title  = "UnHealthyHostCount (Minimum)"
          region = var.aws_region
          period = 60
          metrics = [
            ["AWS/ApplicationELB", "UnHealthyHostCount", "LoadBalancer", local.lb_dim, "TargetGroup", local.tg_dim, { stat = "Minimum" }]
          ]
        }
      },
      {
        type = "metric", x = 0, y = 12, width = 12, height = 6
        properties = {
          title  = "ECS CPUUtilization and MemoryUtilization (percent)"
          region = var.aws_region
          period = 60
          metrics = [
            ["AWS/ECS", "CPUUtilization", "ClusterName", aws_ecs_cluster.this.name, "ServiceName", aws_ecs_service.task_service.name, { stat = "Average" }],
            ["AWS/ECS", "MemoryUtilization", "ClusterName", aws_ecs_cluster.this.name, "ServiceName", aws_ecs_service.task_service.name, { stat = "Average" }]
          ]
          yAxis = { left = { min = 0, max = 100 } }
        }
      },
      {
        type = "metric", x = 12, y = 12, width = 12, height = 6
        properties = {
          title  = "DesiredTaskCount and RunningTaskCount"
          region = var.aws_region
          period = 60
          metrics = [
            ["ECS/ContainerInsights", "DesiredTaskCount", "ClusterName", aws_ecs_cluster.this.name, "ServiceName", aws_ecs_service.task_service.name, { stat = "Average" }],
            ["ECS/ContainerInsights", "RunningTaskCount", "ClusterName", aws_ecs_cluster.this.name, "ServiceName", aws_ecs_service.task_service.name, { stat = "Average" }]
          ]
        }
      }
    ]
  })
}
