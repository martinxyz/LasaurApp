#!/bin/bash

if ! test -r /etc/init.d/pulseraster.sh ; then
    # install
    cp pulseraster.sh /etc/init.d/pulseraster.sh
fi

# disable everything else
test -r /etc/init.d/lasaurapp.sh     && update-rc.d -f lasaurapp.sh remove
test -r /etc/init.d/driveboardapp.sh && update-rc.d -f driveboardapp.sh remove

update-rc.d pulseraster.sh defaults

echo "now type 'reboot'"

