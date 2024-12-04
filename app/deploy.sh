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
echo "Installing Python3, Git, and PIP..."
sudo apt update && sudo apt install -y python3 && sudo apt install -y pip && sudo apt install -y git
check_rc

# Clone Repository
echo "Cloning repository..."
git clone https://github.com/odedra35/dms
check_rc

# Check Repository dir
echo "Checking dms/app dir is present..."
test -d dms/app
check_rc

# Switch to dev branch
echo "Switch to dev branch..."
cd $REPO_DIR
pwd
git switch dev
check_rc

# Install python packages
echo "Installing requirements.txt (breaking)..."
pwd
sudo pip install -r requirements.txt --break-system-packages
check_rc

# Unblock 8080/tcp port using ufw
echo "Unblock ufw port 8080..."
sudo ufw allow 8080/tcp
check_rc

# Run APP in bg
echo "Starting routes.py..."
chmod +x routes.py
python3 routes.py &

exit 0
