
## Setting up


NOTE: The instruction below is shown for MacOS.
1. Install Homebrew [Official page - Homebrew](https://brew.sh/)
   1. `/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"`
2. Install `pyenv`. [PyEnv - Documentation on GitHub](https://github.com/pyenv/pyenv)
   1. `brew install pyenv`
3. Install `Python 3.10.0`
   1. `pyenv install 3.10.0`
4. Install `pyenv-virtualenv`
   1. `brew install pyenv-virtualenv`
5. Create a new virtual environment.
   1. `pyenv virtualenv 3.10.0 bot`
6. Add to your profile (e.g. `~/.zshrc`) `eval "$(pyenv init -)"` to turn on `pyenv`.
7. Restart your Shell
8. To make this interpreter default for this directory 
do `pyenv local bot` in the repo root.
9. `pip install -r requirements.txt`


1. Install Docker from the [Docker official page](https://www.docker.com/)
2. Run the docker container with PostgreSQL database by the command 
`docker run -p 5432:5432 --name some-postgres -e POSTGRES_PASSWORD=mysecretpassword -d postgres`.
The database container must be running so that the bot can work with the database during the game 
or before you are going to create the question table.
You can stop it by `docker stop some-postgres` and rerun by `docker start some-postgres` command.
3. You can also install PgAdmin [here](https://www.postgresql.org/ftp/pgadmin/pgadmin4/) for inspecting the database.
4. Run `populate_db.py` in Terminal to populate a file with questions to DB.
   1. e.g `python populate_db.py [CONTAINER NAME]`
   2. type `python populate_db.py --help` for additional hints