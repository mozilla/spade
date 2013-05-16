# Install python and compiled modules for project
class python {
    case $operatingsystem {
        centos: {
            package {
                ["python-devel",
                 "python-libs",
                 "python-distribute",
                 "python-mod_wsgi",
                 "libatlas-base-dev"]:
                    ensure => installed;
            }

            exec { "pip-install":
                command => "easy_install -U pip",
                creates => "/usr/bin/pip",
                require => Package["python-devel", "python-distribute"]
            }

            exec { "virtualenv-install":
                command => "/usr/bin/pip install -U virtualenv",
                creates => "/usr/bin/virtualenv",
                timeout => 600,
                require => [ Exec['pip-install'] ]
            }

            exec {
                "virtualenv-create":
                cwd => "/home/${APP_USER}",
                user => "vagrant",
                command => "/usr/bin/virtualenv --no-site-packages ${VENV_DIR}",
                creates => $VENV_DIR
            }

            exec { "pip-install-compiled":
                command => "${VENV_DIR}/bin/pip install -r $PROJ_DIR/requirements/compiled.txt",
                require => Exec['virtualenv-create'],
                timeout => 600,
            }
        }

        ubuntu: {
            package {
                ["python-dev", "python", "python-distribute","libapache2-mod-wsgi", "python-wsgi-intercept",  "libxml2-dev", "libxslt1-dev"]:
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
                cwd => "/home/${APP_USER}",
                user => $APP_USER,
                command => "/usr/local/bin/virtualenv --no-site-packages ${VENV_DIR}",
                creates => "${VENV_DIR}"
            }

            exec { 
                "pip-cache-ownership":
                     command => "/bin/chown -R ${APP_USER}:${APP_USER} $PROJ_DIR/puppet/cache/pip && /bin/chmod ug+rw -R $PROJ_DIR/puppet/cache/pip",
                     unless => '/bin/su ${APP_USER} -c "/usr/bin/test -w $PROJ_DIR/puppet/cache/pip"';
                "pip-install-compiled":
                     require => Exec['pip-cache-ownership','virtualenv-create'],
                     user => $APP_USER,
                     cwd => '/tmp', 
                     command => "${VENV_DIR}/bin/pip install --download-cache=$PROJ_DIR/puppet/cache/pip -r $PROJ_DIR/requirements/compiled.txt",
                     timeout => 1200;
            }
        }
    }
}
