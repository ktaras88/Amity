# Amity backend team 2

## The client has requested us to help them to build a B2B platform 
## whose main purpose is to control the stoves at living facilities. 

## Tech details

|**Resource**|**Version**|
| :-: | :-: |
|Python|3.10.5|
|Django|4.1.1|
|Django Rest Framework|3.14.0|
|PostgreSQL|2.9.3|
|Python Decouple |3.6|

> Available Environments:
<br> - <b>Qa</b>
<br> - <b>Production</b>
<br> - <b>Development</b> (for local usage)
---

### Launch a project from Linux/Mac terminal

Add some exports to your shell profile `~/.zshrc` or `~/.bashrc`<br>
Or paste these variables into `.env` file inside the project (without **export**)

```sh
export ENVIRONMENT = local    # environments keys (qa, production, development)

export SECRET_KEY=some_key
```

Restart your terminal for changes to take effect.

Inside the project in terminal:

```sh
pipenv shell
pipenv install

python manage.py runserver
```

> If you do not want to use pipenv but a simple pip, reformat the Pipfile data to requirements.txt valid data.
<br> But it is recommended to use pipenv.
---