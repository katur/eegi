# Installing eegi Project


## Production installation

Here is a walkthrough of how I deployed this with Apache and modwsgi on pyxis (which runs Ubuntu).

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


### MySQL Database

```
mysql -u eegi -p eegi < <sql dump filename>
```


### Code

```
cd /opt/local/eegi
git clone https://github.com/katur/eegi.git

cd /opt/local/eegi/eegi/eegi
# copy local_settings.py from development computer
# edit local_settings with database connection info, setting DEBUG=False
```


### Virtual Environment and Dependencies

```
cd /opt/local/eegi
virtualenv --python=/usr/bin/python2.7 eegivirtualenv
# NOTE: This use of virtualenv hardcodes the name and location of the virtualenv dir.
# But the --relocatable arg has problems and is to be deprecated.
# So, to move or rename it, delete and recreate the virtualenv dir.

source eegivirtualenv/bin/activate
pip install -r eegi/requirements.txt
```


### Collecting Static Files

```
source /opt/local/eegi/eegivirtualenv/bin/activate
cd /opt/local/eegi/eegi
./manage.py collectstatic
```


### Apache Configuration

```
cd /opt/local/eegi
mkdir apache2

vi /opt/local/eegi/apache2/eegi.conf
# add project-specific apache settings, using port 8009
# note that part of this configuration involves serving static files directly
# please see the above file, on pyxis, for details

sudo ln -s /opt/local/eegi/apache2/eegi.conf /etc/apache2/sites-enabled/001-eegi.conf

sudo vi /etc/apache2/ports.conf
# add line to Listen 8009
```


### Apache Commands
```
sudo service apache2 restart
sudo service apache2 start
sudo service apache2 stop
```


### Database Backups
```
mkdir /volume/data1/project/eegi/database_backups

mkdir /opt/local/eegi/secret
chmod 700 /opt/local/eegi/secret

touch /opt/local/eegi/secret/eegi.my.cnf
chmod 600 /opt/local/eegi/secret/eegi.my.cnf
vi /opt/local/eegi/secret/eegi.my.cnf
> [client]
> user = eegi_ro
> password = <password>

mkdir /opt/local/eegi/bin
chmod 775 /opt/local/eegi/bin

vi ~/.zshenv
> path=(/opt/local/eegi/bin $path)
source ~/.zshenv

touch /opt/local/eegi/bin/mysqldump_eegi
chmod 774 /opt/local/eegi/bin/mysqldump_eegi
vi /opt/local/eegi/bin/mysqldump_eegi

> #!/bin/sh
>
> /usr/bin/mysqldump --defaults-file=/opt/local/eegi/secret/eegi.my.cnf --single-transaction eegi | pbzip2 -c -p16 > /volume/data1/project/eegi/database_backups/eegi_`date +%Y-%m-%d_%H-%M-%S`.sql.bz2
```


### Deploying in a Nutshell -- DRAFT

#### *As user eegi...*
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

#### *As user with sudo...*
```
sudo service apache2 restart
```

If front-end changes, inspect visually.
