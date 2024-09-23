#!/bin/bash
echo "Enabling interfaces"
sudo raspi-config nonint do_i2c 0
sudo raspi-config nonint do_serial_hw 0
sudo raspi-config nonint do_serial_cons 1
echo "Interfaces enabled, rebooting"
sudo shutdown --reboot now
sleep 30