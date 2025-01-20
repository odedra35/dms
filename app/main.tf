terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 3.0"
    }
  }
}

# Configure the AWS provider
provider "aws" {
  region = "us-west-2"
}

# Define the first EC2 instance resource
resource "aws_instance" "ec2_prod_one" {
  ami             = "ami-00c257e12d6828491"
  instance_type   = "t2.micro"
  security_groups = ["sg-02b3d29bdcd49a0cc"]

}

# Define the second EC2 instance resource
resource "aws_instance" "ec2_prod_two" {
  ami             = "ami-00c257e12d6828491"
  instance_type   = "t2.micro"
  security_groups = ["sg-02b3d29bdcd49a0cc"]

}

# Data source to get the default VPC
data "aws_vpc" "default_vpc" {
  default = true
}

# Data source to get the subnet IDs of the default VPC
data "aws_subnet_ids" "default_subnet" {
  vpc_id = data.aws_vpc.default_vpc.id
}

# Define the security group for the Application Load Balancer
resource "aws_security_group" "alb" {
  name = "alb-security-group"
}

# Allow inbound HTTP traffic to the ALB
resource "aws_security_group_rule" "allow_alb_http_inbound" {
  type              = "ingress"
  security_group_id = aws_security_group.alb.id
  from_port         = 8080
  to_port           = 8080
  protocol          = "tcp"
  cidr_blocks       = ["0.0.0.0/0"]
}

# Allow all outbound traffic from the ALB
resource "aws_security_group_rule" "allow_alb_all_outbound" {
  type              = "egress"
  security_group_id = aws_security_group.alb.id
  from_port         = 0
  to_port           = 0
  protocol          = "-1"
  cidr_blocks       = ["0.0.0.0/0"]
}

# Define the Application Load Balancer
resource "aws_lb" "load_balancer" {
  name               = "web-app-lb"
  load_balancer_type = "application"
  subnets            = data.aws_subnet_ids.default_subnet.ids
  security_groups    = [aws_security_group.alb.id]
}

# Define the HTTP listener for the ALB
resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.load_balancer.arn
  port              = 80
  protocol          = "HTTP"

  # Default action to return a 404 response
  default_action {
    type = "fixed-response"

    fixed_response {
      content_type = "text/plain"
      message_body = "404: page not found"
      status_code  = 404
    }
  }
}

# Define the target group for the EC2 instances
resource "aws_lb_target_group" "instances" {
  name     = "DMS-target-group"
  port     = 8080
  protocol = "HTTP"
  vpc_id   = data.aws_vpc.default_vpc.id

  # Health check configuration
  health_check {
    path                = "/"
    protocol            = "HTTP"
    matcher             = "200"
    interval            = 15
    timeout             = 3
    healthy_threshold   = 2
    unhealthy_threshold = 2
  }
}

# Attach the first EC2 instance to the target group
resource "aws_lb_target_group_attachment" "ec2_prod_one" {
  target_group_arn = aws_lb_target_group.instances.arn
  target_id        = aws_instance.ec2_prod_one.id
  port             = 8080
}

# Attach the second EC2 instance to the target group
resource "aws_lb_target_group_attachment" "ec2_prod_two" {
  target_group_arn = aws_lb_target_group.instances.arn
  target_id        = aws_instance.ec2_prod_two.id
  port             = 8080
}

# Define the listener rule to forward traffic to the target group
resource "aws_lb_listener_rule" "instances" {
  listener_arn = aws_lb_listener.http.arn
  priority     = 100

  condition {
    path_pattern {
      values = ["*"]
    }
  }

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.instances.arn
  }
}

# Output the public IP address of the first instance
output "ec2_prod_one_public_ip" {
  description = "The public IP address of ec2_prod_one"
  value       = aws_instance.ec2_prod_one.public_ip
}

# Output the public IP address of the second instance
output "ec2_prod_two_public_ip" {
  description = "The public IP address of ec2_prod_two"
  value       = aws_instance.ec2_prod_two.public_ip
}

# Output the DNS name of the load balancer
output "load_balancer_dns" {
  description = "The DNS name of the load balancer"
  value       = aws_lb.load_balancer.dns_name
}