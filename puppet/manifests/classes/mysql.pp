# Get mysql up and running

# mysqldev and mysql service need to be parametrized
# based on the OS
$mysqldev = $operatingsystem ? {
    ubuntu => libmysqld-dev,
    default => mysql-devel
}

$mysqlservice = $operatingsystem ? {
    Amazon => mysqld,
    default => mysql

}

class mysql {
    package { mysql-server:
        ensure => installed
    }

    package { $mysqldev:
        ensure => installed
    }
    service { $mysqlservice:
        ensure => running,
        enable => true,
        require => Package['mysql-server'];
    }
}