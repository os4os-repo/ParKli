# Overview

Der dbupdate-job dient dazu die Dashbaord-Datenbank mit aktuellen Datensätzen aus iNaturalist zu versorgen. Dazu wird zur Laufzeit des Dashboard-Stacks ein weitere Container gestartet der ein Python Sktipt ausführt welches über die iNaturalist-API die Datensätze der letzten 30 Tage in Baden-Württemberg ausließt und die Datensätze in der postgres-Datenbank bei Bedarf aktualisiert/erweitert. Hat der dbupdate-job alle abgefragten Datensätze abgearbeitet, terminiert er wieder bis zum nächsten aufruf. 

![https://github.com/os4os-repo/ParKli/blob/7d4515fa903c4a4dae6e5fe3e209da8e19e65132/images/parkli-dashboard_update.jpg](https://github.com/os4os-repo/ParKli/blob/7d4515fa903c4a4dae6e5fe3e209da8e19e65132/images/parkli-dashboard_update.jpg)

## Installation

The deployment process consists of the following steps:

1. Preparing the config files
2. Build image
3. Deploy containers
4. Create CronJob

### 1. Preparing the config files

After downloading the repository, the env file must be renamed to ‘.env’ (without inverted commas) and the environment variables for the containers must be set in it. The values POSTGRES_DBNAME, POSTGRES_USER and POSTGRES_PASS must be adjusted. All other values can remain at their default values. The same must be done for the dbimport.sh script which is used to load the initial data record into the database. If you have already deployed the dashboard-containers, you can use the existing .env-file.

### 2. Build image

The container for the Dash app must be created using the attached Dockerfile. To do this, change to the directory with the Dockerfile and use the command `docker build . -t parkli-dbupdate/v3 --no-cache` to build a new image. The name of the image can be changed, but must later match the information in the compose file. During the build process, the required additional software from the requirements.txt is installed on top of an existing Python image from the Docker Hub.

### 3. Deploy containers

Once the image and environment variables have been prepared, the job-container can be started. To do this, execute the attached docker-compose.yml with the command `docker compose up` and wait until the stack is running. The output in the terminal should look like this:

![https://github.com/os4os-repo/ParKli/blob/7d2d7052c4bc581a9994a41b499c676521203659/images/start_job_container.PNG](https://github.com/os4os-repo/ParKli/blob/7d2d7052c4bc581a9994a41b499c676521203659/images/start_job_container.PNG)

The first run should take 15-20 minutes. After that, the database is up to date and the container terminates automatically.

### 4. Create CronJob

If you want to update the database automatically, the start of the container must be configured in a CronJob. To do this, open the crontab as admin (`sudo nano /etc/crontab`) and insert the following line to start the container automatically once a day at midnight:

`0  0    * * *   root    /usr/bin/docker compose -f /<PATH TO DOCKER COMPOSE FILE>/docker-compose.yml up -d >/dev/null 2>&1`

To activate the changes, the configuration file must be reloaded:

`sudo service cron reload`
