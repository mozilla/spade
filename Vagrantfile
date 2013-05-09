require "yaml"

# Load up our vagrant config files -- vagrantconfig.yaml first
_config = YAML.load(File.open(File.join(File.dirname(__FILE__),
                    "vagrantconfig.yaml"), File::RDONLY).read)

# Local-specific/not-git-managed config -- vagrantconfig_local.yaml
begin
    _config.merge!(YAML.load(File.open(File.join(File.dirname(__FILE__),
                   "vagrantconfig_local.yaml"), File::RDONLY).read))
rescue Errno::ENOENT # No vagrantconfig_local.yaml found -- that's OK; just
                     # use the defaults.
end

CONF = _config
MOUNT_POINT = '/home/vagrant/project'

Vagrant.configure("2") do |config|
    config.vm.box = "precise32_v"
    config.vm.box_url = "http://files.vagrantup.com/precise32.box"

    config.vm.synced_folder ".", MOUNT_POINT
    config.vm.provision :puppet do |puppet|
        puppet.manifests_path = "puppet/manifests"
        puppet.manifest_file  = "vagrant.pp"
    end
    
    # remote environment provided by aws
    config.vm.provider :aws do |aws, override|
      aws.vm.box = "dummy"
      aws.vm.box_url = "https://github.com/mitchellh/vagrant-aws/raw/master/dummy.box"
      aws.access_key_id = CONF['aws']['access_key_id']
      aws.secret_access_key = CONF['aws']['secret_access_key']
      aws.keypair_name = CONF['aws']['keypair_name']
      aws.ami = CONF['aws']['ami']
      aws.region = CONF['aws']['region']
      aws.security_groups = CONF['aws']["security_groups"]
      override.ssh.username = "vagrant"
      override.ssh.private_key_path = CONF['aws']['private_key_path']
    end

    # local environment provided by virtualbox
    config.vm.provider :virtualbox do |vb, override|
      override.ssh.max_tries = 50
      override.ssh.timeout   = 300

      # nfs needs to be explicitly enabled to run.
      if not CONF['nfs'] == false and not RUBY_PLATFORM =~ /mswin(32|64)/
          config.vm.synced_folder ".", MOUNT_POINT, :nfs => true
      end
      override.vm.network :forwarded_port, guest: 80, host: 8000
      override.vm.network :private_network, ip: "33.33.33.24"
    end
end