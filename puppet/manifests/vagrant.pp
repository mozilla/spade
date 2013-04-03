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
