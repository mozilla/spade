# stage {"pre": before => Stage["main"]} class {'apt': stage => 'pre'}

# Commands to run before all others in puppet.
class init {
    group { "puppet":
        ensure => "present",
    }

    if $operatingsystem == 'ubuntu' {
        exec { "update_apt":
            command => "sudo apt-get update",
        }

        # Provides "add-apt-repository" command, useful if you need
        # to install software from other apt repositories.
        package { "python-software-properties":
            ensure => present,
            require => [
                Exec['update_apt'],
            ];
        }
    }
    file {"/etc/profile.d/spade.sh":
        content => "
export SPADE_DATABASE_NAME='${DB_NAME}'
export SPADE_DATABASE_USER='${DB_USER}'
export SPADE_DATABASE_PASSWORD='${DB_PASS}'
export SPADE_DATABASE_HOST='${DB_HOST}'
export SPADE_DATABASE_PORT='${DB_PORT}'
export SPADE_DEBUG='1'
export SPADE_DJANGO_SECRET_KEY='${DJANGO_SECRET_KEY}'
export RABBITMQ_USER='rabbituser'
export RABBITMQ_PASSWORD='rabbitpass'
export RABBITMQ_VHOST='spade'
"
    }

    exec {"source /etc/profile.d/spade.sh":
        unless => "echo $SPADE_DATABASE_NAME",
        require => File["/etc/profile.d/spade.sh"]
    }
        
}
