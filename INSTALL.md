Installing eegi Project
=======================
Here is a walkthrough of deploying on Ubuntu, with Apache and modwsgi. 

This assumes that most sysadmin setup is already complete.
Lior performed the sysadmin setup on pyxis, and has the documentation.
This sysadmin steps includes the following:

- installing git
- installing Python
- installing virtualenv (for managing Python packages, including Django, within virtual environments)
- installing / setting up MySQL
- installing / setting up Apache
- installing modwsgi
- creating a UNIX user per project (in this case, eegi)
- creating the project directory, owned by the UNIX project user (in this case /opt/local/eegi)
- creating a MySQL user and MySQL database per project (in this case, both named eegi)

MySQL Database
--------------
```
mysql -u eegi -p eegi < <sql dump filename>
```

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

sudo vi /etc/apache2/ports.conf
# add line to Listen 8009
```

Apache Commands
---------------
```
sudo service apache2 restart
sudo service apache2 start
sudo service apache2 stop
```

Deploying in a Nutshell -- DRAFT
--------------------------------
### As user eegi
```
# dump database, in case reverting is necessary
# record the currently-deployed git commit, in case reverting is necessary

# Activate Python virtual environment
cd /opt/local/eegi/eegi
source opt/local/eegi/eegivirtualenv/bin/activate

# Pull changes
git pull

# If changes to requirements.txt:
pip install -r requirements.txt

# If new/changed static files:
./manage.py collectstatic

# If new database migrations:
./manage.py migrate

# If any scripts must be run
./manage.py scriptname

# If there are unit tests:
./manage.py test
```

### As user with sudo
```
sudo service apache2 restart
```

If front-end changes, inspect visually.
