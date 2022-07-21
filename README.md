# Runing
Make sure to update the config file with correct dog and ip address. 

Example:
[DOG_TO_USE]
dog = D1:

[SOCKET]
socket = tcp://192.168.137.80:

This config file is used by the serial daemon to so a systemctl restart serial.daemon.service is needed if its changed!!!