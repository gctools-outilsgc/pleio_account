# Concierge
[![Build Status](https://jenkins.pleio.nl/buildStatus/icon?job=concierge-docker)](https://jenkins.pleio.nl/job/concierge-docker/)

This is the microservice used for handling user registration, login and SAML2 SSO. It is based on the [Django project](https://www.djangoproject.com/).

## Setup development (through Docker)
Make sure [Docker](https://www.docker.com/) and [yarn](https://yarnpkg.com/lang/en/) is installed. Then run the following commands within the repository:

    docker-compose up
    yarn install
    yarn run watch

Then create a superuser account using:

    docker-compose exec web python manage.py createsuperuser

Now login with your new (superuser) account on http://localhost:8000

## Setup development (manually)
To setup the development environment, make sure Python3 and yarn is installed on your development machine. Then run the following commands:

    mkvirtualenv concierge --python=/usr/bin/python3
    pip install -r requirements.txt
    yarn install

Set up and configure a mail server (ex: sendmail)

Make sure postgres is installed and configured and a database is created for your app.

Create your configuration file

    sudo cp concierge/config.example.py concierge/config.py

In your new config file set secret key, allowed hosts, and debug variables. 
Set your database config like:

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'your_database_name',
            'USER': 'Your_database_user',
            'PASSWORD': 'Your_database_password',
            'HOST': '127.0.0.1',
            'PORT': '',
        }
    }

Install a theme and follow any instructions provided by the theme to complete
the installation.

    - [Pleio](https://github.com/Pleio/concierge-theme-pleio)


Create a database using

    python manage.py migrate

Now create a superuser account using:

    python manage.py createsuperuser

Start a yarn and Django server using:

    python manage.py runserver localhost:8000
    yarn run watch

Now login with your new (superuser) account on http://localhost:8000

## Deploy to Kubernetes

    kubectl create namespace concierge
    kubectl create -f ./kubernetes/deployment.yaml

## Generate new translations
We use the standard [i18n toolset of Django](https://docs.djangoproject.com/en/1.10/topics/i18n/). To add new translations to the source files use:

    python manage.py makemessages

To compile the translations use:

    python manage.py compilemessages

On OSX first make sure gettext (> 0.14) is installed and linked using:

    brew install gettext
    brew link --force gettext

## Run tests
To run the accompanied test suite use the following command:

    python manage.py test
