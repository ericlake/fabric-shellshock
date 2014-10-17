#!/usr/bin/env python

from fabric.api import *
from fabric.colors import *

env.connection_attempts = 1
env.command_timeout = 120
env.abort_on_prompts = 1
env.skip_bad_hosts = 1

###############
# Exposed tasks
###############

@task
def hostlist():
    "Prompt for filename of the file containing a list of hosts to hit"
    filename = raw_input("Host list name: ")
    with open(filename, 'r') as f:
        for line in f:
            env.hosts.append(line.strip())

@task
def get_distro_version():
    "Report the distro version of the remote|local system"
    result = run('cat /etc/redhat-release')
    puts(blue(result))
    return result

@task(default=True)
def bash_updater():
    "Test for expoits in bash and update if neccessary"
    os_version = get_distro_version()

    if _check_bash():
        _update_bash(os_version)
        _check_bash()

#################
# "Private" tasks
#################

# All of the expoits to test. The tests being used are from https://shellshocker.net/

def _test_cve_2014_6271():
    output = run('env x="() { :;}; echo vulnerable" bash -c "echo this is a test"')
    return output

def _test_cve_2014_7186():
    output = run('bash -c "true <<EOF <<EOF <<EOF <<EOF <<EOF <<EOF <<EOF <<EOF <<EOF <<EOF <<EOF <<EOF <<EOF <<EOF" || echo "vulnerable"')
    return output

def _test_cve_2014_7187():
    output = run('(for x in {1..200} ; do echo "for x$x in ; do :"; done; for x in {1..200} ; do echo done ; done) | bash || echo "vulnerable"')
    return output

def _test_cve_2014_6278():
    output = run('shellshocker="() { echo vulnerable; }" bash -c shellshocker')
    return output

# End exploit tests

def _is_vulnerable(result, cve_num):
    if 'vulnerable' in result:
        puts(red('Vulnerable %s ' % cve_num))
        vuln = True
    else:
        puts(green('OK %s ' % cve_num))
        vuln = False
    return vuln

def _bash_in_repo():
    """This should only be used for RHEL|CENT 5.x
    RHEL|CENT 6.* should have everything it needs in the repos"""
    version = sudo("yum check-update bash | tail -n 1 | awk '{ print $2 }'")
    if '3.2-33.el5_11.4' in version:
        return True
    else:
        return False

def _install(distro):
    put(distro + '/bash-3.2-33.el5_11.4.x86_64.rpm', '/tmp/bash-3.2-33.el5_11.4.x86_64.rpm')
    sudo('mv /tmp/bash-3.2-33.el5_11.4.x86_64.rpm /root/bash-3.2-33.el5_11.4.x86_64.rpm')
    sudo('yum localinstall -y /root/bash-3.2-33.el5_11.4.x86_64.rpm')
    sudo('rm -f /root/bash-3.2-33.el5_11.4.x86_64.rpm')

def _update_bash(os_version):
    puts(red('Updating bash'))
    sudo('yum clean expire-cache')

    if 'Red Hat' in os_version:
        distro = 'redhat'
    elif 'Cent' in os_version:
        distro = 'centos'

    if '5.' in os_version:
        if distro == 'redhat':
            if not _bash_in_repo():
                # If the rpm is not found in the repos then push it
                _install(distro)
            else:
                sudo('yum update -y bash')
        
        elif distro == 'centos':
            if not _bash_in_repo():
                # If the rpm is not found in the repos then push it
                _install(distro)
            else:
                sudo('yum update -y bash')
        else:
            puts(yellow("Unknows OS for %s" % env.host_string))
    else:
        # If you have made it this far then you must be RHEL|CENT 6
        sudo('yum update -y bash')

def _check_bash():
    for cve in [_test_cve_2014_6278, _test_cve_2014_6271, _test_cve_2014_7186, _test_cve_2014_7187]:
        with settings(
                hide('warnings', 'running', 'stdout', 'stderr'),
                warn_only=True):
            if _is_vulnerable(cve(), cve.func_name):
                return True
    return False

