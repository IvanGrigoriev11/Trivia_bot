
## Setting up


NOTE: The instruction below is shown for MacOS.
1. Install PyCharm from [Official page](https://www.jetbrains.com/pycharm/).
1. Open project
1. Mark directories: `src` - sources root, `tests` - tests root
2. Install Homebrew [Official page - Homebrew](https://brew.sh/).
   1. `/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"`.
1. Install `pyenv`. [PyEnv - Documentation on GitHub](https://github.com/pyenv/pyenv).
   1. `brew install pyenv`.
1. Install `Python 3.10.0`.
   1. `pyenv install 3.10.0`.
1. Install `pyenv-virtualenv`.
   1. `brew install pyenv-virtualenv`.
1. Create a new virtual environment.
   1. `pyenv virtualenv 3.10.0 bot`.
1. Add to your profile (e.g. `~/.zshrc`) `eval "$(pyenv init -)"` to turn on `pyenv`.
1. Restart your Shell.
1. To make this interpreter default for this directory do `cd <repo root>` and execute `pyenv local bot` in the repo root.
1. `pip install -r requirements.txt`.
1. Install Docker from the [Docker official page](https://www.docker.com/).
1. You can also install PgAdmin [here](https://www.postgresql.org/ftp/pgadmin/pgadmin4/) for inspecting the database.


## Populating the database


1. Run the docker container with PostgreSQL database by the command `docker run -p 5432:5432 --name postgres -e POSTGRES_PASSWORD=<the password is the same as used by the bot> -d postgres`. The database container must be running so that the bot can work with the database during the game or before you are going to create the question table. You can stop it by `docker stop postgres` and rerun by `docker start postgres` command.
1. Save your username and password for connecting to docker container in `zshrc` file with name `TRIVIA_POSTGRES_USER=<username>` `TRIVIA_POSTGRES_PASSWD=<password>` so the bot and script files can use it in their purposes later.
1. Run `scrap_opentrivia.py` in `scripts` directory to get a file with questions from OpenTriviaDB.
1. Run `populate_db.py` in Terminal to populate the file with questions to DB.
   1. switch to the repo root and follow to `src/scripts` directory.
   1. `python populate_db.py postgres`. The script gets username and password for connecting to the database from `~./zshrc` file.
   1. type `python populate_db.py --help` for additional hints.


## Launching the bot


1. Run docker container with PostgreSQL by `docker start postgres` if it is stopped. 
1. Switched to the repo root and follow to `src` directory by `cd <repo root>/src`. 
1. Run `python main.py` in Terminal to launch the bot. To connect to the database bot needs to get `TRIVIA_POSTGRES_USER=<username>` `TRIVIA_POSTGRES_PASSWD=<password>` from `~/.zshrc` file.  For more details see `Populating the database` section.
