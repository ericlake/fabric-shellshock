fabric-shellshock
=================

Fabric script to squash the nasty bash shellshock bug

This fabric script should test for CVE-2014-6278, CVE-2014-6271, CVE-2014-7186 and CVE-2014-7187.

There is a redhat and centos directory. Each one contains a gpg signed version of bash for the respective distro. The script will push the file to the server and do a `yum localinstall` on it. Once installed a second test run is made to verify that the vulnerabilities have been patched. Once done then the rpm will be removed.

To Use
------

Create a ~/.fabricrc file in your home directory that looks like the following:

```text
user = ssh_user
```

Then run the fab command with the options that you need. See the examples below.

Command options
---------------
* -I: This prompts for your sudo password
* --hide commands: This keeps the output sane
* -H: Host or list of hosts separated by commas

The script will prompt for 2 or 3 items:
* A filename with a list of hosts to hit (one name per line) if the 'hostlist' option is used
* Your password

In this instance the filename "staging" was used with only one file in it.

```bash
fab hostlist bash_updater -I --hide commands
Initial value for env.password: 
Host list name: staging
[<hostname>] Red Hat Enterprise Linux Server release 5.6 (Tikanga)
[<hostname>] OK test_cve_2014_6278 
[<hostname>] OK test_cve_2014_6271 
[<hostname>] OK test_cve_2014_7186 
[<hostname>] OK test_cve_2014_7187 

Done.
Disconnecting from <hostname>... done.
```

It is possible to specify one host or a list at the command line with the -H option and not using "hostlist". For example:

```bash
fab -H <hostname> -I --hide commands
```

To List Possible Commands
-------------------------

Use `fab --list` or `fab -l`.

```bash
$ fab --list
Available commands:

    bash_updater
    get_distro_version
    hostlist
```

