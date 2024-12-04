#!/bin/bash


# Install Essentials
echo "Installing Python3, Git, and PIP..."
sudo apt update && sudo apt install -y python3 && sudo apt install -y pip && sudo apt install -y git
if [ $? -ne 0 ]; then
  echo "Error: Installing Essentials failed with return code $?"
  exit $?
fi

# Clone Repository
echo "Cloning repository..."
chdir /home/ubuntu/
git clone https://github.com/odedra35/dms
if [ $? -ne 0 ]; then
  echo "Error: Cloning Repository failed with return code $?"
  exit $?
fi

# Check Repository dir
echo "Checking dms/app dir is present..."
test -f dms/app
if [ $? -ne 0 ]; then
  echo "Error: Could not find folder dms/app..."
  exit $?
fi

# Switch to dev branch
echo "Switch to dev branch..."
chdir /home/ubuntu/dms/app
git switch dev
if [ $? -ne 0 ]; then
  echo "Error: Could not git switch to dev branch..."
  exit $?
fi

# Install python packages
echo "Installing requirements.txt (breaking)..."
sudo pip install -r requiremtns.txt --break-system-packages
if [ $? -ne 0 ]; then
  echo "Error: Installing python packages failed with return code $?"
  exit $?
fi

# Unblock 8080/tcp port using ufw
echo "Unblock ufw port 8080..."
sudo ufw allow 8080/tcp
if [ $? -ne 0 ]; then
  echo "Error: Unblocking ufw port 8080 failed with return code $?"
  exit $?
fi

# Run APP in bg
echo "Starting routes.py..."
chmod +x routes.py
python3 routes.py &

exit 0
