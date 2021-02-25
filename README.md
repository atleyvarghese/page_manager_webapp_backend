# Page Manager backend
An API web application designed to list and update facebook page details.

## Setup of development environment

Clone this project:

    $ git clone https://github.com/atleyvarghese/page_manager_webapp_backend.git

It is best to use the python `virtualenv` tool to build locally:

```sh
$ virtualenv -p python3 venv
$ source venv/bin/activate
$ pip install -r requirements.txt
$ source env/local.env
$ python manage.py migrate
```


## Starting app

    $ python manage.py runserver

The app will be served by django **runserver**

Access it through **http://localhost:8000**
