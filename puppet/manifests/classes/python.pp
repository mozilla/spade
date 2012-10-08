# Install python and compiled modules for project
class python {
    case $operatingsystem {
        centos: {
            package {
                ["python26-devel", "python26-libs", "python26-distribute", "python26-mod_wsgi"]:
                    ensure => installed;
            }

            exec { "pip-install":
                command => "easy_install -U pip",
                creates => "/usr/bin/pip",
                require => Package["python26-devel", "python26-distribute"]
            }

            exec { "virtualenv-install":
                command => "/usr/bin/pip install -U virtualenv",
                creates => "/usr/bin/virtualenv",
                timeout => 600,
                require => [ Exec['pip-install'] ]
            }

            exec {
                "virtualenv-create":
                cwd => "/home/vagrant",
                user => "vagrant",
                command => "/usr/bin/virtualenv --no-site-packages /home/vagrant/spade-venv",
                creates => "/home/vagrant/spade-venv"
            }

            exec { "pip-install-compiled":
                command => "/home/vagrant/spade-venv/bin/pip install -r $PROJ_DIR/requirements/compiled.txt",
                require => Exec['virtualenv-create'],
                timeout => 600,
            }
        }

        ubuntu: {
            package {
                ["python2.6-dev", "python2.6", "python-distribute","libapache2-mod-wsgi", "python-wsgi-intercept",  "libxml2-dev", "libxslt1-dev"]:
                    ensure => installed;
            }

            exec { "pip-install":
                command => "/usr/bin/easy_install -U pip",
                creates => "/usr/local/bin/pip",
                require => Package["python-distribute"]
            }
            file { "$PROJ_DIR/puppet/cache/pip":
                    ensure => directory
            }

            exec { "virtualenv-install":
                command => "/usr/local/bin/pip install --download-cache=$PROJ_DIR/puppet/cache/pip -U virtualenv",
                creates => "/usr/local/bin/virtualenv",
                timeout => 600,
                require => [ Exec['pip-install'] ]
            }

            exec {
                "virtualenv-create":
                cwd => "/home/vagrant",
                user => "vagrant",
                command => "/usr/local/bin/virtualenv --no-site-packages /home/vagrant/spade-venv",
                creates => "/home/vagrant/spade-venv"
            }

            exec { 
                "pip-cache-ownership":
                     command => "/bin/chown -R vagrant:vagrant $PROJ_DIR/puppet/cache/pip && /bin/chmod ug+rw -R $PROJ_DIR/puppet/cache/pip",
                     unless => '/bin/su vagrant -c "/usr/bin/test -w $PROJ_DIR/puppet/cache/pip"';
                "pip-install-compiled":
                     require => Exec['pip-cache-ownership','virtualenv-create'],
                     user => "vagrant",
                     cwd => '/tmp', 
                     command => "/home/vagrant/spade-venv/bin/pip install --download-cache=$PROJ_DIR/puppet/cache/pip -r $PROJ_DIR/requirements/compiled.txt",
                     timeout => 1200;
            }
        }
    }
}
