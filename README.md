## Trivia bot 
   The bot plays Trivia game with a user. During the game the bot gives a sequence of questions which the user must answer. The main goal is to get the maximum score for correct answers by the end of the game. This repository contains a Python implementation of a Trivia Telegram bot.

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
   1. `export POSTGRES_DB_USER='postgres'`
   1. `export POSTGRES_DB_PASSWD=<password>`
   1. `export POSTGRES_DB_HOST='localhost'`


## Start the database

The bot relies on being able to connect to database for storing it's state and accessing questions.

1. Run postgres docker container: `docker run -p 5432:5432 --name postgres -e POSTGRES_PASSWORD=$POSTGRES_DB_USER -e POSTGRES_USER=$POSTGRES_DB_PASSWD -d postgres`.
   1. You can stop it by `docker stop postgres` and rerun by `docker start postgres` command.
1. `cd src/scripts`
1. Scrap the questions from OpenTriviaDB `python scrap_opentrivia.py`.
1. Move the scrapped questions to the DB `python populate_db.py populate`


## Launching the bot

1. Ensure postgres docker container is running.
1. `cd <repo_root>/src`
1. `python main.py`


## Creating a docker image 

1. Build the docker image with `docker build --platform=linux/amd64 --tag triviabot .` to create an image based x64 architecture. 


## Running the dockerized bot locally

1. To run the container locally you should create a bridge network for `bot` container to be able to talk to `postgres`
   1. `docker network create --driver bridge bot-net`. It should be done once. After the network creation you can see it in the list by `docker network ls` command. 
1. `docker run --name postgres -e POSTGRES_PASSWORD=$POSTGRES_DB_PASSWD --network bot-net -p 5432:5432 -d postgres` to connect `postgres` container to the network.
1. `docker run -dit -e POSTGRES_DB_USER=$POSTGRES_DB_USER -e POSTGRES_DB_PASSWD=$POSTGRES_DB_PASSWD -e POSTGRES_DB_HOST=$POSTGRES_DB_HOST -e POSTGRES_DB_NAME=$POSTGRES_DB_NAME -e TELEGRAM_BOT_TOKEN=$TELEGRAM_BOT_TOKEN --name bot --network bot-net triviabot` to connect your docker image to the network and run bot locally.
1. `docker network inspect bot-net` to check if the containers are connected properly. Below this command the information about connection will be represented. You have to see `Containers` key where there are two lists dedicated to `postgres` and `bot` containers with their IP addresses. If both are shown there, everything is ok with the connection. 
1. Do the additional checks from [this tutorial](https://docs.docker.com/network/network-tutorial-standalone/#use-user-defined-bridge-networks) to be make sure the connection is good by pinging it.
   1. While your containers are running in the background, use `docker attach` command to connect each container alternately. i.e. for the `postgres` container:
      1. `docker attach postgres`
      1. `ping -c 2 google.com`
      1. `ping -c 2 bot`
      1. `ping -c 2 <IP address of bot>`
      1. Detach from `postgres` without stopping it by using the detach sequence, <CTRL+p> <CTRL+q> (hold down CTRL and type p followed by q).
      1. Repeat the same steps for `bot` container.


## Configure environment variables for running the bot on AWS

The bot relies on environment to get DB credentials. Launching the database and the bot assumes the below variables are set.

   1. `export POSTGRES_DB_USER="postgres"`
   1. `export POSTGRES_DB_PASSWD=<password>`
   1. `export POSTGRES_DB_HOST="triviabotdb.cuiy2vsvegcs.eu-central-1.rds.amazonaws.com"`
   1. `export POSTGRES_DB_NAME="initial_db"`
   1. `export TELEGRAM_BOT_TOKEN=<bot token>`
  
 
## Launching the bot on AWS

### Prerequisites
1. Before you launch `bot` on AWS, see the section `Creating a docker image` above.
1. Use the existing resources below by following the links:
   1. [Ubuntu VM](https://eu-central-1.console.aws.amazon.com/ec2/home?region=eu-central-1#InstanceDetails:instanceId=i-0e19f4912725d17f4)
   1. [RDS instance](https://eu-central-1.console.aws.amazon.com/rds/home?region=eu-central-1#database:id=triviabotdb;is-cluster=false)
   1. [ECR](https://eu-central-1.console.aws.amazon.com/ecr/repositories?region=eu-central-1)
1. If the database is empty, populate your json file with questions to AWS database by `python populate_db.py populate` from <repo_root>/src/scripts.
1. If you build the docker `bot` image with the latest updates, push it to AWS repository following [this tutorial](https://docs.aws.amazon.com/AmazonECR/latest/userguide/docker-push-ecr-image.html).
   1. `aws ecr get-login-password --region eu-central-1 | docker login --username AWS --password-stdin 158048943261.dkr.ecr.eu-central-1.amazonaws.com`.
   1. `docker images`
   1. `docker tag c6acad0a810d 158048943261.dkr.ecr.eu-central-1.amazonaws.com/trivia_bot:latest`
   1. `docker push 158048943261.dkr.ecr.eu-central-1.amazonaws.com/trivia_bot:latest`
1. Run your VM. Connect to your VM using SSH and:
   1. If any of the resources below do not exist, follow the links and install it once: 
      1. [Install Docker engine](https://docs.docker.com/engine/install/).
      1. [Install AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html).
      1. [Configure AWS Credentials](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-quickstart.html#cli-configure-quickstart-config).
   1. Authenticate with AWS ECR by `aws ecr get-login-password --region eu-central-1 | docker login --username AWS --password-stdin 158048943261.dkr.ecr.eu-central-1.amazonaws.com`.
   1. Pull your docker image using `docker pull 158048943261.dkr.ecr.eu-central-1.amazonaws.com/trivia_bot:latest`.
1. Configure environment variables in your VM. 
1. `docker run -p 5432:5432 -e POSTGRES_DB_USER=$POSTGRES_DB_USER -e POSTGRES_DB_PASSWD=$POSTGRES_DB_PASSWD -e POSTGRES_DB_HOST=$POSTGRES_DB_HOST -e POSTGRES_DB_NAME=$POSTGRES_DB_NAME -e TELEGRAM_BOT_TOKEN=$TELEGRAM_BOT_TOKEN --name triviabot 158048943261.dkr.ecr.eu-central-1.amazonaws.com/trivia_bot:latest`.