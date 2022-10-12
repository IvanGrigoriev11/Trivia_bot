
## Setting up


**NOTE**: The instruction below is shown for MacOS.
1. Install Homebrew [Official page - Homebrew](https://brew.sh/).
   1. `/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"`.
1. Install `pyenv`. [PyEnv - Documentation on GitHub](https://github.com/pyenv/pyenv).
   1. `brew install pyenv`.
   1. Add to your profile (e.g. `~/.zshrc`) `eval "$(pyenv init -)"` to turn on `pyenv`.
1. Install `Python 3.10.0`.
   1. `pyenv install 3.10.0`.
1. Install `pyenv-virtualenv`.
   1. `brew install pyenv-virtualenv`.
1. Create a new virtual environment.
   1. `pyenv virtualenv 3.10.0 bot`.
1. Restart your Shell.
1. To make this interpreter default for the project
   1. `cd <repo root>`
   1. run `pyenv local bot`
1. Install the requirements: `pip install -r requirements.txt`.
1. Install Docker from the [Docker official page](https://www.docker.com/).
1. Optinally install PgAdmin [here](https://www.postgresql.org/ftp/pgadmin/pgadmin4/) for inspecting the database.


## Configure the IDE
1. Install PyCharm from [Official page](https://www.jetbrains.com/pycharm/).
1. Open the repo root as a new project.
1. Mark directories: `src` - sources root, `tests` - tests root. Right click to do so.
1. Set `pyenv bot` as the project interpreter.


## Configure environment variables

The bot relies on environment to get DB credentials. Launching the database and the bot assumes the below variables are set.

1. Set `TRIVIA_POSTGRES_USER` and `TRIVIA_POSTGRES_PASSWD` environemnt variables. Put them in your profile (e.g. `.zshrc`)
   1. `export TRIVIA_POSTGRES_USER=<user>`
   1. `export TRIVIA_POSTGRES_PASSWD<password>`


## Start the database

The bot relies on being able to connect to database for storing it's state and accessing questions.


1. Run postgres docker container: `docker run -p 5432:5432 --name postgres -e POSTGRES_PASSWORD=$TRIVIA_POSTGRES_USER -e POSTGRES_USER=$TRIVIA_POSTGRES_PASSWD -d postgres`.
   1. You can stop it by `docker stop postgres` and rerun by `docker start postgres` command.
1. `cd src/scripts`
1. Scrap the questions from OpenTriviaDB `python scrap_opentrivia.py`.
1. Move the scrapped questions to the DB `python populate_db.py postgres`


## Launching the bot


1. Ensure postgres docker container is running.
1. `cd <repo_root>/src`
1. `python main.py`
