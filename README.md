# ECS

The ethic commission system (ECS) is an open-source webservice supporting clinical trials approval, monitoring and the electronic management of the related data. See the [ECS Homepage](https://ecs-org.github.io/ecs-docs/) for more information about ECS.


**See the [Administrator Manual](https://ecs-org.github.io/ecs-docs/admin-manual/index.html) for installing and configuring an ECS-Appliance.**


## Development

The devserver requires at least 10GB Harddisk Space and 1,5GB RAM.

### using Vagrant

If you use vagrant, clone this repository to your local machine, add [vagrant-password-growroot.iso](https://raw.githubusercontent.com/ecs-org/cidata-seed/master/vagrant-password-growroot.iso) as `seed.iso` inside the root directory of the repository and execute `vagrant up`.

### Installing the devserver to an empty xenial vm

+ install an empty ubuntu xenial server/cloud image from: [Ubunu Xenial Cloud Images](http://cloud-images.ubuntu.com/xenial/current/)

+ configure ssh access to the cloud image by copying [vagrant-password-growroot.iso](https://raw.githubusercontent.com/ecs-org/cidata-seed/master/vagrant-password-growroot.iso) as `seed.iso`

    + to use your own ssh key, build a new cidata iso by using: [github.com/ecs-org/cidata-seed](https://github.com/ecs-org/cidata-seed/)

+ login via ssh and execute

```
# install git, clone ecs repository and start bootstrap-devserver.sh script
apt-get -y update && apt-get -y install git
mkdir -p /app/ecs; git clone https://github.com/ecs-org/ecs /app/ecs
chmod +x /app/ecs/scripts/*.sh; /app/ecs/scripts/bootstrap-devserver.sh --yes
```

+ alternative, using only the bootstrap script:
```
curl https://raw.githubusercontent.com/ecs-org/ecs/master/scripts/bootstrap-devserver.sh > /tmp/bootstrap.sh
chmod +x /tmp/bootstrap.sh; /tmp/bootstrap.sh --yes
```

## Using the devserver

+ login into devserver and forward port 8000 (django http) to your local machine:
    + `ssh -L 8000:localhost:8000 app@virtual.machine`
    
+ start devserver `sudo systemctl start devserver`
  + once started, the devserver will be available under http://localhost:8000

+ stop devserver: `sudo systemctl stop devserver`
  
+ look into logfile of devserver:
    + show devserver logfile with paging: `sudo journalctl -u devserver`
    + follow the log to see errors or emails: `sudo journalctl -u devserver -f`
    + search for user emails retrospective:
        + `sudo journalctl -u devserver | grep href`
        + `sudo journalctl -u devserver | grep ': Subject' -A 25`
    + grep something in the log: `sudo journalctl -u devserver | grep -i migration`

+ django management:
```
. ~/env/bin/activate
cd ~/ecs
./manage.py
```

### using devupdate.sh 

Features:

+ updates/restarts everything needed for the requested change without intervention
+ allows only one running devupdate at a time, second will abort
+ automatically restores from dump if needed


Usage:

+ **get help**: execute `devupdate.sh`

+ install all app and server dependencies, do not touch sourcecode
    + `devupdate.sh init`

+ fetch changes, checkout last used branch, update server
    + `devupdate.sh pull`

+ fetch changes, force checkout last used branch, restore from dump, update server
    + `devupdate.sh --restore-dump pull --force`

+ fetch changes, checkout to another branch, update server
    + `devupdate.sh pull foobranch`

+ use a empty database with testusers for screencasts
    + change to a different branch if needed: `devupdate.sh pull branchname`
    + clear database, add testuser: `ECS_USERSWITCHER_PARAMETER=-it devupdate.sh freshdb`

+ dump current database, will be saved to /app/ecs.pgdump and will be preferred on restore over default iso dump
    + `devupdate.sh dumpdb`
+ dump current database to a custom filename:
    + `devupdate.sh dumpdb mydump.pgdump`
+ restore from custom dump (use absolute filenames for dumpfilename):
    + `ECS_DUMP_FILENAME=~/mydump.pgdump devupdate.sh --restore-dump init`
+ clone an existing database dump available via ssh into the devserver database
    + `devupdate.sh transferdb root@domain.name cat /data/ecs-pgdump/ecs.pgdump.gz`
+ make a new database dump on a remote machine and transfer this dump via ssh into the devserver database
    + `devupdate.sh transferdb root@domain.name "gosu app /bin/bash -c 'set -o pipefail && pg_dump --encoding=utf-8 --format=custom -Z0 -d ecs | /bin/gzip --rsyncable'"`
+ disable updates, branch switches & database restores
    + `touch /app/devupdate.disabled`
    + to remove this lock: `rm /app/devupdate.disabled`
