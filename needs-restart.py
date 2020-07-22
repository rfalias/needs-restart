#!/usr/bin/env python
# title           :needs_restart.py
# description     :Show services that need restarting
# author          :jstevenson
# date            :07/14/2020
# version         :0.1
# usage           :python needs_restarting.py
# notes           :Uses lsof to look for pending deleted .so files, and maps the pid to service
# python_version  :> 2.x
#==============================================================================
import os
import argparse

# Setup Parser
parser = argparse.ArgumentParser(description='Show or fix services that need restarting after updates')
parser.add_argument('-s','--show', action="store_true", default=False, help="Just show which services need restarting")
parser.add_argument('-f','--fix', action="store_true", default=False, help="Restart services that need it")
parser.add_argument('-e','--exclude', nargs='+', help="Optional services to exclude from restarting")


# Show items needing restart. Maps output from lsof to systemctl
def show_needs_restart():
    stream = os.popen('lsof')
    output = stream.readlines()
    restart_list = list()
    for x in output:
        sp = x.split()
        op = sp[4]
        if "DEL" in op:
            fi = sp[8]
            if ".so" in fi:
                svc =  os.popen('systemctl status ' + sp[2])
                svc_out = svc.readlines()
                if ".service" in svc_out[0]:
                    unit = svc_out[0].split()[1]
                    if unit not in restart_list:
                        restart_list.append(unit)

    return restart_list


# Take the list from show_needs_restart and issue the systemctl restart command
# auditd must use service, its a known issue with RHEL.
def do_restart(exclude):
    restart_list = show_needs_restart()
    tmp_list = list()
    for service in restart_list:
        if (service in exclude):
            print("Skipping %s, in exclude list" % service)
            continue
        if "auditd.service" in service:
            print("Restarting auditd using 'service' command. See RHEL Solution 2664811")
            os.system("/sbin/service auditd stop")
            os.system("/bin/systemctl start auditd")
        else:

            print("Restarting " + service)
            os.system("/bin/systemctl restart " + service)
        tmp_list.append(service)
    if len(restart_list) > 0:
        os.system("/bin/systemctl restart systemd-*")
    for x in tmp_list:
        restart_list.remove(x)
    if len(restart_list) > 0:
        print("Some services were not be restarted (Exclusion or failure): ")
        for y in restart_list:
            print(y)
    else:
        print("All services restarted successfully")
        for x in show_needs_restart():
            print(x)


# Check the args and setup defaults as needed
def check_args(args):
    if not (args.show or args.fix):
        print("Action required, --show or --fix")
        exit(-1)
    if args.show:
        for x in show_needs_restart():
            print(x)
    if args.fix:
        exclude_list = list()
        if args.exclude:
            exclude_list = args.exclude
        do_restart(exclude_list)


if __name__ == "__main__":
    if os.geteuid() != 0:
        exit("You need to have root privileges to run this script.")
    if not (os.path.isfile('/sbin/service')
            and os.path.isfile('/bin/systemctl')
            and os.path.isfile('/sbin/lsof')):
        exit("Missing dependencies, check for lsof, service and systemctl")
    args = parser.parse_args()
    check_args(args)
