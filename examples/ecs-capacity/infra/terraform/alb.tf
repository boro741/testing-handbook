# Application Load Balancer, target group and listener. The VPC and subnets already exist.

resource "aws_security_group" "alb" {
  name        = "${var.name_prefix}-alb"
  description = "Allow the load generator to reach the ALB"
  vpc_id      = var.vpc_id

  ingress {
    description = "HTTP from approved CIDRs"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = var.allowed_ingress_cidrs
  }

  egress {
    description = "To the tasks"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_lb" "this" {
  name               = "${var.name_prefix}-alb"
  load_balancer_type = "application"
  internal           = false
  security_groups    = [aws_security_group.alb.id]
  subnets            = var.alb_subnet_ids
}

resource "aws_lb_target_group" "task_service" {
  name        = "${var.name_prefix}-ts"
  port        = var.container_port
  protocol    = "HTTP"
  target_type = "ip" # required for Fargate awsvpc tasks
  vpc_id      = var.vpc_id

  health_check {
    path                = var.health_check_path
    matcher             = "200"
    interval            = 15
    timeout             = 5
    healthy_threshold   = 2
    unhealthy_threshold = 3
  }
}

resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.this.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.task_service.arn
  }
}
