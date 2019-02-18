* Scraper Python software for Chilean Miner data.

* * Requirements
- Python > 2.7
- virtualenv
- - ``sudo apt-get install virtualenv``
- MySql Server
- - ``sudo apt-get install mysql-server``
- - ``sudo apt-get install libmysqlclient-dev``

* * Create a virtual environment for each python projects
  - Clone this project and make a container dir for this:
  - - ``mkdir prev``
  - - ``mv Extraccion_Minera prev``
  - Then virtualize this current environment using
  - - ``virtualenv /prev``

* * Install requirements of the projects
  - `` pip install -r requirements.txt ``
  
* * Create project Database
  - `` mysql -u <user> -p``
  - `` CREATE DATABASE <database_name>;``
  - `` \q``

* * Create a ``.env`` file in the root of the project that will contain the following environment variables
  - ``USER=<database_username>``
  - ``PASSWORD=<database_password>``
  - ``NAME=<database_name>``
  - ``HOST=<database_host_or_ip>``

* * Migrate Database
  - ``honcho run python manage.py migrate``
  - ``honcho run python manage.py createsuperuser``

* * Run project development mode
  - ``honcho run python manage.py runserver``
  - You can see it, by default: ``http://localhost:8000``

* * Stop server using
  - `` deactivate ``
  - or ``Ctrl + C``
  