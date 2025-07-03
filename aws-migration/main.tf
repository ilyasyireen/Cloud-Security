provider "aws" {
  region = "us-east-1"
}

# VPC
resource "aws_vpc" "hotel_vpc" {
  cidr_block = "10.0.0.0/16"
  tags = {
    Name = "Hotel-Booking-VPC"
  }
}

# Public Subnet (for ALB/EC2)
resource "aws_subnet" "public_subnet" {
  vpc_id     = aws_vpc.hotel_vpc.id
  cidr_block = "10.0.1.0/24"
  availability_zone = "us-east-1a"
  tags = {
    Name = "Public-Subnet"
  }
}

# Private Subnet (for RDS)
resource "aws_subnet" "private_subnet" {
  vpc_id     = aws_vpc.hotel_vpc.id
  cidr_block = "10.0.2.0/24"
  availability_zone = "us-east-1b"
  tags = {
    Name = "Private-Subnet"
  }
}

# Internet Gateway
resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.hotel_vpc.id
  tags = {
    Name = "Hotel-IGW"
  }
}

# Route Table (Public)
resource "aws_route_table" "public_rt" {
  vpc_id = aws_vpc.hotel_vpc.id
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.igw.id
  }
}

# ALB
resource "aws_lb" "hotel_alb" {
  name               = "hotel-booking-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb_sg.id]
  subnets            = [aws_subnet.public_subnet.id]
}

# EC2 Instance (Django App)
resource "aws_instance" "django_app" {
  ami           = "ami-0c55b159cbfafe1f0"  # Ubuntu 20.04 LTS
  instance_type = "t2.micro"
  subnet_id     = aws_subnet.public_subnet.id
  user_data     = file("user_data.sh")  # Script to install Django
  tags = {
    Name = "Django-App-Server"
  }
}

# RDS (PostgreSQL)
resource "aws_db_instance" "hotel_db" {
  identifier           = "hotel-booking-db"
  engine               = "postgres"
  instance_class       = "db.t3.micro"
  allocated_storage    = 20
  db_name              = "hotel_booking"
  username             = var.db_username
  password             = var.db_password
  vpc_security_group_ids = [aws_security_group.rds_sg.id]
  db_subnet_group_name = aws_db_subnet_group.hotel_db_subnet.name
  skip_final_snapshot  = true
}

# Security Groups
resource "aws_security_group" "alb_sg" {
  name        = "alb-security-group"
  description = "Allow HTTP/HTTPS to ALB"
  vpc_id      = aws_vpc.hotel_vpc.id

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_security_group" "rds_sg" {
  name        = "rds-security-group"
  description = "Allow PostgreSQL from EC2"
  vpc_id      = aws_vpc.hotel_vpc.id

  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.ec2_sg.id]
  }
}