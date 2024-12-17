#!/bin/bash
#

# Exit on rc != 0
check_rc () {
  if [ $? -ne 0 ]; then
    echo "Error: failed with return code $?"
    exit $?
  fi
}

REPO_DIR="/home/ubuntu/dms/app"

# Install Essentials
echo "Installing Python3, Git, PIP, and Docker..."
sudo -i
apt update && apt install -y python3 && apt install -y pip && apt install -y git && apt install -y docker.io
check_rc

# Clone Repository
echo "Cloning repository..."
git clone -b dev https://github.com/odedra35/dms
check_rc

# Check Repository dir
echo "Checking dms/app dir is present..."
test -d dms/app
check_rc

# Switch to dev branch
#echo "Switch to dev branch..."
#cd $REPO_DIR
#pwd
#git switch dev
#check_rc

# Install python packages
echo "Installing requirements.txt (breaking)..."
cd $REPO_DIR
pwd
pip install -r requirements.txt --break-system-packages --ignore-installed
check_rc

# Unblock 8080/tcp port using ufw
echo "Unblock ufw port 8080..."
ufw allow 8080/tcp
check_rc

# Run APP in bg
echo "Starting routes.py..."
chmod +x routes.py
python3 routes.py

exit 0
