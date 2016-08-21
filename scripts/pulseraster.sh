#!/bin/bash
# place in: /etc/init.d/pulseraster.sh
# make executable: sudo chmod 755 /etc/init.d/pulseraster.sh
# activate with: sudo update-rc.d pulseraster.sh defaults
# deactivate with: sudo update-rc.d -f pulseraster.sh remove

if test "$1" = "start"
then
    echo "Starting Pulseraster backend..."
    (
      cd /root/pulseraster/backend
      /usr/bin/python3 backend.py beaglebone.ini
    )
fi
