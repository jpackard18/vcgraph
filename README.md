# Veracross Graph
A Graphical Representation of Academic Perfomance Extrapolated from the Veracross Student Portal with Score Objectives for Upcoming Assignments

## Getting Started
These instructions will help you set up a working copy of Veracross Graph on your system. I highly recommend using a Python virutal environment for the installation. If you are looking to host a live version, see the deployment section below.

### Prerequisites
* Python >= 3.6.0
* Pip
* Django
* Requests-Futures
* BeautifulSoup

### Installation
Enter your vcgraph directory and create & activate your Python virtual environment
```
$ cd path/to/vcgraph
$ python3 -m venv vcgraphenv
$ source vcgraphenv/bin/activate
```
Once the virtual environment has been created, install the necessary packages
```
(vcgraphenv) $ pip install django requests-futures bs4
```
Create the database file and a superuser account with the following three commands
```
(vcgraphenv) $ python manage.py makemigrations
(vcgraphenv) $ python manage.py migrate
(vcgraphenv) $ python manage.py createsuperuser
```
After entering a username and password, use the following command to generate a random secret key
```
(vcgraphenv) $ python -c "import random; print(''.join(random.SystemRandom().choice('abcdefghijklmnopqrstuvwxyz0123456789! @#$%^&*(-_=+)'.replace(' ','')) for i in range(50)))"
```
This will create a 50 character long random string that you must set as the value of SECRET_KEY in [vcgraph/settings.py](https://github.com/jpackard18/vcgraph/blob/master/vcgraph/settings.py#L23).
Finally, you can run the server by typing
```
(vcgraphenv) $ python manage.py runserver
```
This will start the server locally on port 8000 and will not be accessable by any other computers on your network.
## Deployment

### Prerequisites
* Apache2
* Apache2-dev
* Mod-WSGI

### Installation
Install mod_wsgi within your Python virtual environment
```
(vcgraphenv) $ pip install mod_wsgi
```
Get the LoadModule and PythonHome settings for your Apache Configuration (you'll need this for the next step)
```
(vcgraphenv) $ mod_wsgi-express module-config
LoadModule wsgi_module "/path/to/vcgraph/vcgraphenv/lib/python3.6/site-packages/mod_wsgi/server/mod_wsgi-py36.cpython-36m-arm-linux-gnueabihf.so"
WSGIPythonHome "/path/to/vcgraph/vcgraphenv"
```
Create an Apache configuration file for vcgraph (using SSL is highly recommended)
```
$ sudo nano /etc/apache2/sites-available/vcgraph.conf
```
```
# First two lines are the output of the previous command
LoadModule wsgi_module "/path/to/vcgraph/vcgraphenv/lib/python3.6/site-packages/mod_wsgi/server/mod_wsgi-py36.cpython-36m-arm-linux-gnueabihf.so"
WSGIPythonHome "/path/to/vcgraph/vcgraphenv"
<IfModule mod_ssl.c>
<VirtualHost _default_:443>
	# The ServerName directive sets the request scheme, hostname and port that
	# the server uses to identify itself. This is used when creating
	# redirection URLs. In the context of virtual hosts, the ServerName
	# specifies what hostname must appear in the request's Host: header to
	# match this virtual host. For the default virtual host (this file) this
	# value is not decisive as it is used as a last resort host regardless.
	# However, you must set it for any further virtual host explicitly.
	#ServerName www.example.com

	ServerAdmin webmaster@localhost
	DocumentRoot /var/www/html

        Alias /static /path/to/vcgraph/static
        <Directory /path/to/vcgraph/static>
            Require all granted
        </Directory>

        <Directory /path/to/vcgraph/vcgraph>
            <Files wsgi.py>
                Require all granted
            </Files>
        </Directory>

        WSGIDaemonProcess vcgraph python-path=/path/to/vcgraph python-home=/path/to/vcgraph/vcgraphenv
        WSGIProcessGroup vcgraph
        WSGIScriptAlias / /path/to/vcgraph/vcgraph/wsgi.py

	# Available loglevels: trace8, ..., trace1, debug, info, notice, warn,
	# error, crit, alert, emerg.
	# It is also possible to configure the loglevel for particular
	# modules, e.g.
	#LogLevel info ssl:warn

	ErrorLog ${APACHE_LOG_DIR}/error.log
	CustomLog ${APACHE_LOG_DIR}/access.log combined

        SSLEngine on
        
        SSLCertificateFile      /path/to/apache.crt
        SSLCertificateKeyFile /path/to/apache.key

        BrowserMatch "MSIE [2-6]" \
                               nokeepalive ssl-unclean-shutdown \
                               downgrade-1.0 force-response-1.0

	# For most configuration files from conf-available/, which are
	# enabled or disabled at a global level, it is possible to
	# include a line for only one particular virtual host. For example the
	# following line enables the CGI configuration for this host only
	# after it has been globally disabled with "a2disconf".
	#Include conf-available/serve-cgi-bin.conf
</VirtualHost>
</IfModule>
```
Finally, enable the site and reload Apache
```
$ sudo a2ensite vcgraph
$ sudo service apache2 reload
```
## Authors
* __James Packard__ '18 - [jamespackard.me](https://jamespackard.me)

## Acknowledgments
* Brandon Li '17 - GPA Calculation, Contacting the school - [Strikingly](http://brandonli.strikingly.com)
* Nikhil Patel '18 - Brilliant Login Page Photos - [Photography](https://npatelphotography.myportfolio.com)
* Saint John's Prep - [Website](https://www.stjohnsprep.org)
* Veracross - [Website](https://www.veracross.com)
