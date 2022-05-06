#!/bin/bash
sudo -u nkhatiwada DISPLAY=:0 DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus /usr/bin/notify-send 'Please update the events for tomorrow.' 'A schedule will be printed in half an hour' -t 30000 -u normal -i appointment-new
date | tr '\n' ' ' > /home/nkhatiwada/Timemanagement/timelog &&  echo "     Notified to update events.txt file for tomorrow" >> /home/nkhatiwada/Timemanagement/timelog
