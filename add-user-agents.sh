#!/bin/sh

# Add some user-agent strings.

# Add iPhone 3.0
./manage.py useragents --add "Mozilla/5.0 (iPhone; U; CPU iPhone OS 3_0 like Mac OS X; en-us) AppleWebKit/528.18 (KHTML, like Gecko) Version/4.0 Mobile/7A341 Safari/528.16" --name "iPhone 3.0"

# Add chrome android from galaxy nexus
./manage.py useragents --add "Mozilla/5.0 (Linux; U; Android 4.0.4; Galaxy Nexus Build/IMM76B) AppleWebkit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.133 Mobile Safari/535.19" --name "Chrome 18, Galaxy Nexus"

# Add fennec UA
./manage.py useragents --add "Mozilla/5.0 (Android; Mobile; rv:18.0) Gecko/18.0 Firefox/18.0" --primary --name "Fennec 18.0"

# Add desktop firefox
./manage.py useragents --add "Mozilla/5.0 (Windows NT 6.1; rv:18.0) Gecko/20120716 Firefox/18.0" --desktop --name "Firefox Desktop 18.0 Windows"

# Add android stock UA
./manage.py useragents --add "Mozilla/5.0 (Linux; U; Android 4.0.2; en-US; Galaxy Nexus Build/ICL53F) AppleWebKit/535.7 (KHTML, like Gecko) CrMo/16.0.912.75 Mobile Safari/535.7" --name "Android ICS Stock"

# Add firefox os
./manage.py useragents --add "Mozilla/5.0 (Mobile; rv:18.0) Gecko/18.0 Firefox/18.0" --name "Firefox OS gecko: 18"
