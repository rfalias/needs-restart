# needs-restart
Script to check which RHEL based distro services need to be restarted after a yum update

Optionally fix them.
```
python needs-restart.py --show
dbus.service
polkit.service
```

Run with --fix to restart all services. Optional --exclude takes a list of services to exclude from restarting
```
python needs-restart.py --fix --exclude dbus.service
Skipping dbus.service, in exclude list
Restarting polkit.service
Some services were not be restarted (Exclusion or failure):
dbus.service
````
