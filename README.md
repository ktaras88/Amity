# Amity backend team 2

## The client has requested us to help them to build a B2B platform whose main purpose is to control the stoves at living facilities

## General URL’s

|**Provider**|**Service Name**|**URL**|
| :- | :- | :- |
|Hosting provider|AWS||
|CI/CD provider|CircleCI||
|Email provider|||
|DNS provider|||
|SSL storage|||
|Logs provider|||
|Error handling provider|Sentry|| 
|Performance monitoring provider|||
|Git workflow|Google Drive||
|Code checker|SonarQube||

## Application URL’s

|**Environment**|**Service Name**|**URL**|
| :- | :- | :- |
|Production|Website||
||Swagger||
||Admin Panel||
|Staging|Website||
||Swagger||
||Admin Panel||
|QA|Website||
||Swagger||
||Admin Panel||

## Tech details

|**Resource**|**Resource Name**|**Version**|**Comment**|
| :-: | :-: | :-: | :-: |
|Back-end programming language|Python|3.10.5||
|Back-end web framework|Django|4.1.1||
|REST APIs toolkit|Django Rest Framework|3.14.0||
|Database|PostgreSQL|2.9.3||
|Web server||||


> Available Environments:
<br> - <b>Qa</b>
<br> - <b>Production</b>
<br> - <b>Development</b> (for local usage)
---

## Installation & Lunch

How to run a project locally?

1. Preparing

Install pipenv

```sh
pipenv shell
pipenv install
```

2. Start server

```sh
python manage.py runserver
```

3. Stop server

```sh
Ctrl+C
```

4. Run migrations or database schema 
```sh
./manage.py migrate
```
6. Run unit tests 

```sh
./manage.py test
```

## Managing environment variables

Add some exports to your shell profile `~/.zshrc` or `~/.bashrc`<br>
Or paste these variables into `.env` file inside the project (without **export**)

```sh
export ENVIRONMENT = local    # environments keys (prod, local)

export SECRET_KEY=some_key

export DB_NAME = your_db_name ('amity')
export DB_USER_NAME = your_user_name
export DB_PASSWORD = your_password
export DB_HOST = your_db_host
export DB_PORT = your_port_to_db (5432)
export ALLOWED_HOSTS = your_allowed_hosts []
export STATIC_URL = 'static/'

export DSN_KEY = your_key
export EMAIL_HOST_USER = your_host_user
export EMAIL_HOST_PASSWORD = your_email_for_host_user

export FRONT_END_DOMAIN_URL = your_domain_url
export FRONT_END_NEW_PASSWORD_PART = '/auth/create_new_password'

export AWS_ACCESS_KEY_ID = your_aws_access_key
export AWS_SECRET_ACCESS_KEY = your_aws_secret_access_key
export AWS_STORAGE_BUCKET_NAME = your_aws_storage_bucket_name
```

Restart your terminal for changes to take effect.
