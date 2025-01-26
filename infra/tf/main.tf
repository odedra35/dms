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
resource "aws_instance" "dms-jenkins" {
  ami             = "ami-05d38da78ce859165"
  instance_type   = "t2.micro"
  vpc_security_group_ids = ["sg-02b3d29bdcd49a0cc"]
  key_name       = "Moni"
  tags = {
    Name        = "DMS-Jenkins"
    DMS     = "jenkins" 
    Group = "DMS"
  }
}

# Define the second EC2 instance resource
resource "aws_instance" "dms-docker" {
  ami             = "ami-05d38da78ce859165"
  instance_type   = "t2.micro"
  vpc_security_group_ids = ["sg-02b3d29bdcd49a0cc"]
  key_name       = "Moni"
    tags = {
    Name        = "DMS-Jenkins-Docker"
    DMS     = "jenkins-docker" 
    Group = "DMS"
  }
}

resource "aws_instance" "dms-ansible" {
  ami             = "ami-05d38da78ce859165"
  instance_type   = "t2.micro"
  vpc_security_group_ids = ["sg-02b3d29bdcd49a0cc"]
  key_name       = "Moni"
    tags = {
    Name        = "DMS-Jenkins-Ansible"
    DMS     = "jenkins-ansible" 
    Group = "DMS"
  }
}

resource "aws_instance" "dms-prod1" {
  ami             = "ami-05d38da78ce859165"
  instance_type   = "t2.micro"
  vpc_security_group_ids = ["sg-02b3d29bdcd49a0cc"]
  key_name       = "Moni"
    tags = {
    Name        = "DMS-prod1"
    DMS     = "dms-prod" 
    Group = "DMS"
  }
}

resource "aws_instance" "dms-prod2" {
  ami             = "ami-05d38da78ce859165"
  instance_type   = "t2.micro"
  vpc_security_group_ids = ["sg-02b3d29bdcd49a0cc"]
  key_name       = "Moni"
    tags = {
    Name        = "DMS-prod2"
    DMS     = "dms-prod" 
    Group = "DMS"
  }
}

data "aws_vpc" "default_vpc" {
  default = true
}

data "aws_subnet_ids" "default_subnet" {
  vpc_id = data.aws_vpc.default_vpc.id
}

# Define the Application Load Balancer
resource "aws_lb" "load_balancer" {
  name               = "dms"
  load_balancer_type = "application"
  subnets            = data.aws_subnet_ids.default_subnet.ids
  security_groups    = ["sg-02b3d29bdcd49a0cc"]
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
    matcher             = "302"
    interval            = 15
    timeout             = 3
    healthy_threshold   = 2
    unhealthy_threshold = 2
  }
   stickiness { 
    type = "lb_cookie" 
    cookie_duration = 86400 # 1 day in seconds 
    }
}

# Attach the first EC2 instance to the target group
resource "aws_lb_target_group_attachment" "dms-prod1" {
  target_group_arn = aws_lb_target_group.instances.arn
  target_id        = aws_instance.dms-prod1.id
  port             = 8080
}

# Attach the second EC2 instance to the target group
resource "aws_lb_target_group_attachment" "dms-prod2" {
  target_group_arn = aws_lb_target_group.instances.arn
  target_id        = aws_instance.dms-prod2.id
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

# # Null resource to run Ansible
# resource "null_resource" "ansible_provision" {
#   provisioner "local-exec" {
#     # command = "ansible-playbook -i '${aws_instance.example.public_ip},' playbook.yaml"
#     command = "ansible-playbook -i inventory_aws_ec2.yaml playbook.yaml"
#   }

#   # Triggers Ansible when the instance changes
#   triggers = {
#     instance_id = aws_instance.example.id
#   }
# }

resource "null_resource" "ansible_play" {
  depends_on = [
    aws_instance.dms-ansible,
    aws_instance.dms-docker,
    aws_instance.dms-jenkins,
    aws_instance.dms-prod1,
    aws_instance.dms-prod2,
  ]

  provisioner "local-exec" {
      command = "ansible-playbook -i inventory_aws_ec2.yaml playbook.yaml"
  }
}


# Output the public IP address of the first instance
output "dms-jenkins" {
  description = "The public IP address of dms-jenkins"
  value       = aws_instance.dms-jenkins.public_ip
}

# Output the public IP address of the second instance
output "dms-docker" {
  description = "The public IP address of dms-docker"
  value       = aws_instance.dms-docker.public_ip
}

output "dms-ansible" {
  description = "The public IP address of dms-ansible"
  value       = aws_instance.dms-ansible.public_ip
}

output "dms-prod1" {
  description = "The public IP address of dms-prod1"
  value       = aws_instance.dms-prod1.public_ip
}

output "dms-prod2" {
  description = "The public IP address of dms-prod2"
  value       = aws_instance.dms-prod2.public_ip
}
# Output the DNS name of the load balancer
output "load_balancer_dns" {
  description = "The DNS name of the load balancer"
  value       = aws_lb.load_balancer.dns_name
}