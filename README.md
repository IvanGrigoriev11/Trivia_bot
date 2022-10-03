
## Setting up

1. Install `conda`. [Miniconda — Conda documentation](https://docs.conda.io/en/latest/miniconda.html)
2. Create virtual environment with Python `3.10`
    1. `conda env create --name bot`
    2. `conda activate bot`
    3. `conda install python=3.10`
    4. `pip install -r requirements.txt`
3. Install `PyCharm`
4. Open project
5. Configure interpreter to be from the environment (2)
6. Mark directories
    1. `src` - sources root
    2. `tests` - tests root

or

1. Install `pyenv`. [PyEnv - Documentation on GitHub](https://github.com/pyenv/pyenv)
   1. `brew install pyenv`
2. Install `Python 3.10.4`
   1. `pyenv install 3.10.4`
3. Install `pyenv-virtualenv`
   1. `brew install pyenv-virtualenv`
4. Create a new virtual environment.
   1. `pyenv virtualenv 3.10.4 bot`
5. Add in `~/.zshrc` line to enable auto-activation of virtual environment:
   1. `open ~/.zshrc`
   2. `eval "$(pyenv init -)"`
   3. Reload the Terminal
6. Add in `~/.zshrc` line to assign the name `bot` to concrete directory.
   1. `open ~/.zshrc`
   2. `alias bot='cd ~/projects/Trivia_bot`
   3. Reload the Terminal
7. `pip install -r requirements.txt`


1. Install Docker from the [Docker official page](https://www.docker.com/)
2. Install PostgreSQL as a special Docker container for [the following instruction](https://hub.docker.com/_/postgres)
   1. Do not forget to map a port for your postgres instance,
   for example `-p 5432:5432` to your `run` command
3. Install PgAdmin4 [here](https://www.postgresql.org/ftp/pgadmin/pgadmin4/)
4. Run `populate_db.py` in Terminal to populate a file with questions to DB.
   1. e.g `python populate_db.py [CONTAINER NAME]`
   2. type `python populate_db.py --help` for additional hints