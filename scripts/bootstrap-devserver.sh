#!/bin/bash

usage(){
    cat << EOF
Usage:  $0 --yes

installs everything needed for a devserver setup.

EOF
    exit 1
}

if test "$1" != "--yes"; then usage; fi

export DEBIAN_FRONTEND=noninteractive
export LANG=en_US.UTF-8

timedatectl set-timezone "Europe/Vienna"
locale-gen en_US.UTF-8 de_DE.UTF-8 &&  dpkg-reconfigure locales
printf "LANG=en_US.UTF-8\nLANGUAGE=en_US:en\nLC_MESSAGES=POSIX\n" > /etc/default/locale

for i in apt-daily.service apt-daily.timer unattended-upgrades.service; do
    systemctl disable $i
    systemctl stop $i
    ln -sf /dev/null /etc/systemd/system/$i
done

apt-get -y update
# cloud-initramfs-growroot will grow root partition (p1) to max volume size (after a reboot)
apt-get -y install software-properties-common cloud-initramfs-growroot acpid git

export HOME=/app
adduser --disabled-password --gecos ",,," --home "/app" app
cp -r /etc/skel/. /app/.
echo "app ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/90-app-sudo
echo "Defaults env_keep+='http_proxy'" > /etc/sudoers.d/10-env-http-proxy
echo "Defaults env_keep+=SSH_AUTH_SOCK" > /etc/sudoers.d/10-env-ssh-auth-sock
if test ! -f /app/ecs; then
    git clone https://github.com/ecs-org/ecs /app/ecs
fi
mkdir -p /app/bin
ln -sft /app/bin /app/ecs/scripts/*
chown -R app:app /app
chmod +x /app/ecs/scripts/*.sh

# devupdate: setup all, create an empty database and a fallback dump
sudo -H -E -u app -- /bin/bash -c ". /app/.profile; cd /app/ecs; ./scripts/devupdate.sh init; ./scripts/devupdate.sh dumpdb $HOME/ecs-pgdump-fallback/ecs.pgdump"
