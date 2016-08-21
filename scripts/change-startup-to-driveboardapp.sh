#!/bin/bash

if ! test -r /etc/init.d/driveboardapp.sh ; then
    echo "Cannot switch: /etc/init.d/driveboardapp.sh is not installed!"
    exit 1
fi

# disable everything else
test -r /etc/init.d/pulseraster.sh   && update-rc.d -f pulseraster.sh remove
test -r /etc/init.d/lasaurapp.sh     && update-rc.d -f lasaurapp.sh remove

update-rc.d driveboardapp.sh defaults

echo "now type 'reboot'"

