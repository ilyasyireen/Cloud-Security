#!/bin/bash
# Install dependencies
apt-get update
apt-get install -y git python3-pip postgresql-client

# Clone repo (replace with your actual repo)
git clone https://github.com/ilyasyireen/Cloud-Security.git
cd /home/ubuntu/Secure_Hotel_Booking_System

# Install requirements
pip3 install -r requirements.txt psycopg2-binary

# Migrate DB (this will auto-create tables)
python3 manage.py migrate

# Run server
python3 manage.py runserver 0.0.0.0:8000