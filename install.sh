#!/bin/bash
echo "Installing dependencies"
sudo apt -y update
sudo apt -y install git gammu python3-gammu ppp python3-serial python3-smbus python3-pika python3-numpy

echo "Generating device secret"
chars=0123456789
secret=
for i in {1..6}
do
    secret+=${chars:RANDOM%${#chars}:1}
done
echo "Your device secret is: $secret"
echo "Save it somewhere, it will be needed to connect with your phone later"

echo "Configure your device"
echo -n "APN: "
read -r APN
echo -n "Device phone number (format '+YYXXXXXXXXX'): "
read -r deviceNumber
echo -n "RabbitMQ host: "
read -r rabbitHost
echo -n "RabbitMQ user: "
read -r rabbitUser
echo -n "RabbitMQ password: "
read -r rabbitPassword

echo "Copying configuration files"
sudo cp ./installation_files/gammurc /etc/gammurc
sudo cp ./installation_files/rnet /etc/ppp/peers/rnet
sudo sed -i "s/NETWORK_APN/$APN/g" /etc/ppp/peers/rnet
cp ./installation_files/template_config.json ./config.json
sed -i "s/DEVICE_SECRET/$secret/g" ./config.json
sed -i "s/DEVICE_NUMBER/$deviceNumber/g" ./config.json
sed -i "s/RABBIT_HOST/$rabbitHost/g" ./config.json
sed -i "s/RABBIT_USER/$rabbitUser/g" ./config.json
sed -i "s/RABBIT_PASSWORD/$rabbitPassword/g" ./config.json

echo "Copying executables"
sudo mkdir -p /usr/local/sbin/Anti-theft-GPS-system
sudo cp ./{*.py,config.json} /usr/local/sbin/Anti-theft-GPS-system/

echo "Installing accelerometer library"
git clone https://github.com/H2BGroup/DFRobot_LIS.git
sudo cp -r DFRobot_LIS/python/raspberrypi/examples/LIS2DW12/activity_detect /usr/local/sbin/Anti-theft-GPS-system/

echo "Creating service"
sudo cp ./installation_files/anti_theft_gps_system.service /etc/systemd/system/anti_theft_gps_system.service
sudo systemctl daemon-reload
sudo systemctl enable anti_theft_gps_system
echo "Starting application"
sudo systemctl start anti_theft_gps_system

echo "Anti-theft GPS system was installed successfully"