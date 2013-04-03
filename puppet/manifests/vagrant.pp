#
# Playdoh puppet magic for dev boxes
#
import "classes/*.pp"

$PROJ_DIR = "/home/vagrant/project"

# You can make these less generic if you like, but these are box-specific
# so it's not required.

$DB_NAME = "spade"
$DB_USER = "spade_user"
$DB_PASS = "spade_pass"
$DB_HOST = "localhost"
$DB_PORT = "3306"
$DJANGO_SECRET_KEY = "5up3r53cr3t"
$RABBITMQ_USER = "rabbituser"
$RABBITMQ_PASSWORD = "rabbitpass"
$RABBITMQ_VHOST = "spade"

Exec {
    path => "/usr/local/bin:/usr/bin:/usr/sbin:/sbin:/bin",
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
"
}


class dev {
    class {
        init: before => Class[mysql];
        mysql: before  => Class[python];
        python: before => Class[apache];
        apache: before => Class[spade];
        spade: before => Class[rabbitmq];
        rabbitmq:;

    }
}

include dev
