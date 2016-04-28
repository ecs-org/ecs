# -*- mode: ruby -*-
# vi: set ft=ruby :
Vagrant.configure(2) do |config|

  config.vm.box = "wily"
  config.vm.define "ecs"

  config.vm.synced_folder ".", "/app/ecs", type: "rsync", rsync__exclude: ""
  config.ssh.forward_agent = true

  if Vagrant.has_plugin?("vagrant-proxyconf")
    if "#{ENV['http_proxy']}" != ""
      config.proxy.http  = "#{ENV['http_proxy']}"
    end
  end

  config.vm.provider "libvirt" do |lv, override|
    lv.memory = 2048
    lv.cpus = 4
    lv.disk_bus = "virtio"
    lv.nic_model_type = "virtio"
    lv.keymap = "de-de"
  end

  config.vm.provider "virtualbox" do |vb, override|
    vb.memory = 2048
    vb.cpus = 4
    override.vm.box_url = "http://cloud-images.ubuntu.com/vagrant/wily/current/wily-server-cloudimg-amd64-vagrant-disk1.box"
  end

  config.vm.provision "shell", privileged:true, inline: <<-SHELL
    # https://github.com/mitchellh/vagrant/issues/5673
    hostnamectl set-hostname ecs.local
    export DEBIAN_FRONTEND=noninteractive
    apt-get -y update
    apt-get -y install software-properties-common spice-vdagent cloud-initramfs-growroot
    apt-get -y upgrade
    apt-get -y dist-upgrade
  SHELL

  if Vagrant.has_plugin?("vagrant-reload")
    config.vm.provision :reload
  end

  config.vm.provision "shell", privileged:true, inline: <<-SHELL
    resize2fs /dev/vda2
    exit 0
    # take the oportunity to resize, may and will fail depending setup, so exit 0
  SHELL

  config.vm.provision "shell", privileged:true, inline: <<-SHELL
    export LANG=en_US.UTF-8
    printf %b "LANG=en_US.UTF-8\nLANGUAGE=en_US:en\nLC_MESSAGES=POSIX\n" > /etc/default/locale
    locale-gen en_US.UTF-8 && dpkg-reconfigure locales

    export HOME=/app
    adduser --disabled-password --gecos ",,," --home "/app" app
    for a in storage-vault log cache ca help gpg undeliverable-mail whoosh; do
      mkdir -p /app/ecs-$a
    done
    chown -R app /app
    chmod +x /app/ecs/scripts/*.sh

    # install system dependencies with local postgres
    cd /app/ecs/ && ./scripts/install-os-deps.sh --with-postgres-server
    # install user dependencies
    gosu app bash -c 'cd /app/ecs && ./scripts/install-user-deps.sh /app/env'
    # devserver: do not write a version.py file
  SHELL

end
