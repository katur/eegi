Installing eegi Project
=======================
Here is a walkthrough of an Ubuntu deploy, using Apache
and modwsgi. WORK IN PROGRESS.


MySQL Database
--------------
```
mysql -u eegi -p eegi < <sql dump filename>
```

<!---
```
DROP DATABASE IF EXISTS eegi;
CREATE DATABASE eegi;
USE eegi;

DROP USER eegi;
CREATE USER 'eegi'@'%' IDENTIFIED BY '<password>';
GRANT ALL PRIVILEGES ON eegi.* TO 'eegi'@'%' IDENTIFIED BY '<password>';
```
-->

Code
----
```
cd /opt/local/eegi
git clone https://github.com/katur/eegi.git
cd /opt/local/eegi/eegi/eegi
# copy local_settings.py from development computer
# edit local_settings with database connection info, and set DEBUG=False
```

Virtual Environment and Dependencies
------------------------------------
```
cd /opt/local/eegi
virtualenv --python=/usr/bin/python2.7 eegivirtualenv
# NOTE: This use of virtualenv hardcodes the name and location of the virtualenv dir.
# But the --relocatable arg has problems and is to be deprecated.
# So, to move or rename it, delete and recreate the virtualenv dir.
source eegivirtualenv/bin/activate
pip install -r eegi/requirements.txt
```

Static Files
------------
```
source /opt/local/eegi/eegivirtualenv/bin/activate
cd /opt/local/eegi/eegi
./manage.py collectstatic
```

Running Django Built-in Development Server
------------------------------------------
```
source /opt/local/eegi/eegivirtualenv/bin/activate
/opt/local/eegi/eegi/manage.py runserver <IP address>:8000
```

Apache Configuration
--------------------
```
cd /opt/local/eegi
mkdir apache2
cd apache2
vi eegi.conf
# add project-specific apache settings, using port 8009
sudo ln -s /opt/local/eegi/apache2/eegi.conf /etc/apache2/sites-enabled/001-eegi.conf
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

Deploying (to be fleshed out and automated)
-------------------------------------------
```
### As user eegi...
# dump database, in case reverting is necessary
# record the currently-deployed git commit, in case reverting is necessary
cd /opt/local/eegi/eegi
source opt/local/eegi/eegivirtualenv/bin/activate
git pull
# if requirements.txt changed:
pip install -r requirements.txt
# if new database migrations:
./manage.py migrate
# if any scripts must be run, e.g. to modify data in keeping with schema changes:
./manage.py scriptname
# if unit tests:
./manage.py test

### As user katherine...
sudo service apache2 restart
# if front-end changes, visual inspection of site
# if necessary, revert the repo, db, and packages to the recorded versions.
```
