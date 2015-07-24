Deploying eegi Project
======================
Here is a walkthrough of an Ubuntu deploy, using Apache
and modwsgi. WORK IN PROGRESS.


MySQL Database
--------------
```
DROP DATABASE IF EXISTS eegi;
CREATE DATABASE eegi;
USE eegi;

DROP USER eegi;
CREATE USER 'eegi'@'%' IDENTIFIED BY '<password>';
GRANT ALL PRIVILEGES ON eegi.* TO 'eegi'@'%' IDENTIFIED BY '<password>';
```

Code
----
```
cd /opt/local/eegi
mkdir staging
cd /opt/local/eegi/staging
git clone https://github.com/katur/eegi.git
cd /opt/local/eegi/staging/eegi/eegi
# copy local_settings.py from development computer
# edit local_settings with database connection info, and set DEBUG=False
```

Virtual Environment and Dependencies
------------------------------------
```
cd /opt/local/eegi/staging
virtualenv --python=/usr/bin/python2.7 eegivirtualenv
source eegivirtualenv/bin/activate
pip install -r eegi/requirements.txt
```

Running Django Built-in Development Server
------------------------------------------
```
./manage.py runserver <IP address>:8000
```

Apache Configuration
--------------------
```
cd /opt/local/eegi/staging
mkdir apache2
cd apache2
vi eegi.conf
# add project-specific apache settings, using port 8009 for staging
sudo ln -s /opt/local/eegi/staging/apache2/eegi.conf /etc/apache2/sites-enabled/001-eegi.conf
cd /etc/apache2
vi ports.conf
# add line to Listen 8009. comment out line to Listen 80 if port 80 not being used
```

Apache Commands
---------------
```
sudo service apache2 restart
sudo service apache2 start
sudo service apache2 stop
```
