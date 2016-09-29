# -*- mode: ruby -*-
# vi: set ft=ruby :

require 'fileutils'
Vagrant.require_version ">= 1.6.0"

# Variables, can be overwritten by vagrant-include.rb
$cpus = 2
$memory = 1500
$ecs_rsync_vagrant_source = true
$ecs_git_source = "https://github.com/ethikkom/ecs.git"
$ecs_git_branch = "master"
$libvirt_management_network_name = "vagrant-libvirt"
$libvirt_management_network_address = ""
$libvirt_management_network_mac = nil
$libvirt_machine_virtual_size = 10
$clouddrive_path = nil
$ecs_pgdump_iso = nil
$devserver_name = File.basename(File.expand_path(File.dirname(__FILE__)))

CUSTOM_CONFIG = File.join(File.dirname(__FILE__), "vagrant-include.rb")
if File.exist?(CUSTOM_CONFIG)
  require CUSTOM_CONFIG
end


Vagrant.configure(2) do |config|

  config.vm.box = "xenial"
  config.vm.define "ecs"

  config.ssh.forward_agent = true

  config.vm.synced_folder ".", "/vagrant", type: "rsync", disabled: true
  if $ecs_rsync_vagrant_source
    config.vm.synced_folder ".", "/app/ecs", type: "rsync", create: true, rsync__exclude: "", rsync__auto: false
  end
  if Dir.exist?(File.join(File.dirname(__FILE__), './local'))
    config.vm.synced_folder "./local", "/app/.devserver-local", type: "rsync", create: true, rsync__exclude: "", rsync__auto: false
  end

  if Vagrant.has_plugin?("vagrant-proxyconf")
    if "#{ENV['http_proxy']}" != ""
      config.proxy.http  = "#{ENV['http_proxy']}"
    end
  end

  config.vm.provider "libvirt" do |lv, override|
    lv.memory = $memory
    lv.cpus = $cpus
    lv.disk_bus = "virtio"
    lv.nic_model_type = "virtio"
    lv.video_type = 'vmvga'
    lv.volume_cache = 'none'
    lv.management_network_name = $libvirt_management_network_name
    lv.management_network_address = $libvirt_management_network_address
    lv.machine_virtual_size = $libvirt_machine_virtual_size
    if $libvirt_management_network_mac
      lv.management_network_mac = $libvirt_management_network_mac
    end
    if $clouddrive_path
      lv.storage :file, :device => :cdrom, :allow_existing => true, :path => $clouddrive_path
    end
    if $ecs_pgdump_iso
      lv.storage :file, :device => :cdrom, :allow_existing => true, :path => $ecs_pgdump_iso
    end
  end

  config.vm.provider "virtualbox" do |vb, override|
    vb.memory = $memory
    vb.cpus = $cpus
    override.vm.box_url = "http://cloud-images.ubuntu.com/xenial/current/xenial-server-cloudimg-amd64-vagrant.box"
    # TODO: clouddrive cdrom inclusion for virtualbox with 'customize ["modifyvm", ...'
  end

  config.vm.provision "shell", privileged:true, inline: <<-SHELL
    # https://github.com/mitchellh/vagrant/issues/5673
    hostnamectl set-hostname #{$devserver_name}.local
    echo "127.0.0.1 #{$devserver_name}.local ecs.local" >> /etc/hosts
    timedatectl set-timezone "Europe/Vienna"
    export DEBIAN_FRONTEND=noninteractive
    export LANG=en_US.UTF-8
    printf %b "LANG=en_US.UTF-8\nLANGUAGE=en_US:en\nLC_MESSAGES=POSIX\n" > /etc/default/locale
    locale-gen en_US.UTF-8 de_DE.UTF-8 && dpkg-reconfigure locales
    echo "==> Disabling the release upgrader"
    sed -i.bak 's/^Prompt=.*$/Prompt=never/' /etc/update-manager/release-upgrades
    apt-get -y update
    # cloud-initramfs-growroot will grow root partition (p1) to max volume size (after a reboot)
    apt-get -y install software-properties-common spice-vdagent cloud-initramfs-growroot git
    apt-get -y dist-upgrade --force-yes
  SHELL

  if Vagrant.has_plugin?("vagrant-reload")
    config.vm.provision :reload
  end

  config.vm.provision "shell", privileged:true, inline: <<-SHELL
    # create user
    export HOME=/app
    adduser --disabled-password --gecos ",,," --home "/app" app
    # manual copy because /app/ecs might exist from ecs source rsync, and adduser does not copy on existing home dir
    cp -r /etc/skel/. /app/.

    # add user app to sudoers
    echo "app ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/90-app-sudo
    # keep http_proxy and ssh_agent env by default
    echo "Defaults env_keep+='http_proxy'" > /etc/sudoers.d/10-env-http-proxy
    echo "Defaults env_keep+=SSH_AUTH_SOCK" > /etc/sudoers.d/10-env-ssh-auth-sock

    # symlink scripts to ~/bin
    mkdir -p /app/bin
    ln -sft /app/bin /app/ecs/scripts/*

    # chown files
    chown -R app:app /app

    # source .devserver-local overrides early
    if test -f /app/.devserver-local/local-override-early.sh; then
      . /app/.devserver-local/local-override-early.sh
    fi

    # clone source if not rsynced by vagrant
    if test ! -f /app/ecs; then
      pushd /app
      sudo -H -E -u app -- /bin/bash -c "git clone --branch #{$ecs_git_branch} #{$ecs_git_source} ecs"
      popd
    fi

    # source .local overrides late
    if test -f /app/.devserver-local/local-override-late.sh; then
      . /app/.devserver-local/local-override-late.sh
    fi

    # automount ecs-pgdump-iso if exists
    grep -Eq "LABEL=ecs-pgdump-iso" /etc/fstab
    if test $? -ne 0; then
      echo "LABEL=ecs-pgdump-iso  /app/ecs-pgdump-iso  iso9660 defaults,ro,nofail  0 0" >> /etc/fstab
      systemctl daemon-reload
    fi

    # devupdate: setup all, create an empty database and a fallback dump
    sudo -H -E -u app -- /bin/bash -c ". /app/.profile; cd /app/ecs; ./scripts/devupdate.sh init; ./scripts/devupdate.sh dumpdb $HOME/ecs-pgdump-fallback/ecs.pgdump"

    echo "finished"
  SHELL

end
