
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


## Configure environment variables for running bot locally

The bot relies on environment to get DB credentials. Launching the database and the bot assumes the below variables are set.

1. Set `POSTGRES_DB_USER` and `POSTGRES_DB_PASSWD` environment variables. Put them in your profile (e.g. `.zshrc`)
   1. `export POSTGRES_DB_USER=<user>`
   1. `export POSTGRES_DB_PASSWD=<password>`


## Start the database

The bot relies on being able to connect to database for storing it's state and accessing questions.


1. Run postgres docker container: `docker run -p 5432:5432 --name postgres -e POSTGRES_PASSWORD=$POSTGRES_DB_USER -e POSTGRES_USER=$POSTGRES_DB_PASSWD -d postgres`.
   1. You can stop it by `docker stop postgres` and rerun by `docker start postgres` command.
1. `cd src/scripts`
1. Scrap the questions from OpenTriviaDB `python scrap_opentrivia.py`.
1. Move the scrapped questions to the DB `python populate_db.py postgres`


## Launching the bot


1. Ensure postgres docker container is running.
1. `cd <repo_root>/src`
1. `python main.py`


## Creating a docker image 


1. Build the docker file by the command `docker build --platform=linux/arm64 --platform=linux/amd64 --tag triviabot .` to create a multiplatforming image based ARM and x64 architecture. 
1. To run the container locally you should create user-defined bridge networks with `postgres` container. 
   1. `docker network create --driver bridge bot-net`. It should be done once. After the network creation you can see it in the list by `docker network ls` command. 
   1. `docker run -p 5432:5432 -dit -e POSTGRES_PASSWORD=$POSTGRES_DB_USER -e POSTGRES_USER=$POSTGRES_DB_PASSWD --name postgres --network bot-net` to connect `postgres` container to the network.
   1. `docker run -dit -e POSTGRES_DB_USER=$POSTGRES_DB_USER -e POSTGRES_DB_PASSWD=$POSTGRES_DB_PASSWD -e POSTGRES_DB_HOST="localhost" -e POSTGRES_DB_NAME=postgres --name bot --network bot-net triviabot` to connect your docker image to the network and run bot locally.
   1. `docker network inspect bot-net` to check if the containers are connected properly. 
   1. Follow [this tutorial](https://docs.docker.com/network/network-tutorial-standalone/#use-user-defined-bridge-networks) for additional connection check.


## Configure environment variables for running the bot on AWS


The bot relies on environment to get DB credentials. Launching the database and the bot assumes the below variables are set.

   1. `export POSTGRES_DB_USER=<user>`
   1. `export POSTGRES_DB_PASSWD=<password>`
   1. `export POSTGRES_DB_HOST=<host name>`
   1. `export POSTGRES_DB_NAME=<database name>`
   1. `export TELEGRAM_BOT_TOKEN=<bot token>`
  
 
## Launching the bot on AWS

### Prerequisites
1. Before you launch `bot` on AWS, see the section `Creating a docker image` above.
1. Create AWS account [on the official page](https://aws.amazon.com/). **NOTE**: Choose the same region here and below. 
1. Launch an Ubuntu VM and connect to it via ssh.
1. Create an AWS Postgres instance.
1. Create a private ECR repository in your AWS account.

###
1. Populate your json file with questions to AWS database by `python populate_db.py` from <repo_root>/src/scripts.
1. Push your docker `bot` image to AWS repository following [this tutorial](https://docs.aws.amazon.com/AmazonECR/latest/userguide/docker-push-ecr-image.html).
1. Run your VM. Connect to your VM using SSH and:
   1. [Install Docker engine](https://docs.docker.com/engine/install/).
   1. [Install AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html).
   1. [Configure AWS Credentials](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-quickstart.html#cli-configure-quickstart-config).
   1. Authenticate with AWS ECR by `aws ecr get-login-password --region eu-central-1 | docker login --username AWS --password-stdin <your aws account_id>.dkr.ecr.eu-central-1.amazonaws.com`.
   1. Pull your docker image using `docker pull <your aws account_id>.dkr.ecr.eu-central-1.amazonaws.com/trivia_bot:lately`.
1. Configure environment variables in your VM. 
1. `docker run -p 5432:5432 -e POSTGRES_DB_USER=$POSTGRES_DB_USER -e POSTGRES_DB_PASSWD=$POSTGRES_DB_PASSWD -e POSTGRES_DB_HOST=$POSTGRES_DB_HOST -e POSTGRES_DB_NAME=$POSTGRES_DB_NAME -e TELEGRAM_BOT_TOKEN=$TELEGRAM_BOT_TOKEN --name triviabot <your aws account_id>.dkr.ecr.eu-central-1.amazonaws.com/trivia_bot:lately`.