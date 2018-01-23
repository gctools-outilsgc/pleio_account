# Pleio account
This is the Pleio microservice used for handling user registration, login and SAML2 SSO. It is based on [Django project](https://www.djangoproject.com/) and handles login througout the Pleio ecosystem using OAuth2.

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

    mkvirtualenv pleio_account --python=/usr/bin/python3
    pip install -r requirements.txt
    yarn install

Create a database using

    python manage.py migrate

Now create a superuser account using:

    python manage.py createsuperuser

Start a yarn and Django server using:

    python manage.py runserver localhost:8000
    yarn run watch

Now login with your new (superuser) account on http://localhost:8000

## Generate new translations
We use the standard [i18n toolset of Django](https://docs.djangoproject.com/en/1.10/topics/i18n/). To add new translations to the source files use:

    python manage.py makemessages

To compile the translations use:

    python manage.py compilemessages

On OSX first make sure gettext (> 0.14) is installed and linked using:

    brew install gettext
    brew link --force gettext

## Run tests
To run the accompanied test suite use:

    python manage.py test
