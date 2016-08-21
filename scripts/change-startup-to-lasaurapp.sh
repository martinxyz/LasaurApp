#!/bin/bash

if ! test -r /etc/init.d/lasaurapp.sh ; then
    echo "Cannot switch: /etc/init.d/lasaurapp.sh is not installed!"
    exit 1
fi

# disable everything else
test -r /etc/init.d/pulseraster.sh   && update-rc.d -f pulseraster.sh remove
test -r /etc/init.d/driveboardapp.sh && update-rc.d -f driveboardapp.sh remove

update-rc.d lasaurapp.sh defaults

echo "now type 'reboot'"

