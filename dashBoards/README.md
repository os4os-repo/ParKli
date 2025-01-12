# Parkli DashBoards

The aim of the ParKli research project is to make the consequences of climate change on local natural and living spaces tangible through citizen science activities and to (further) develop local early warning systems for climate protection together with citizens. By collecting, analysing and illustrating environmental data, local changes and correlations will be investigated.

The ParKli services were developed step by step in a Co-creation process, and one of the questions was. How can the different data that is collected be visualised and analysed?
For example, requirements were defined by the citizen scientists involved, which were implemented step by step by the ParKli team. One requirement was that users should not be concerned with aggregating and collating the data, but should instead focus on analysing it. Various APPs and sensors were used in ParKli to collect data.

The artefacts developed are published in this repository. We are aware that it can be better organised, so we are constantly improving our documentation. If you have any questions or suggestions, please contact us.

Further information can be found here: www.parkli.de

The ParKli research project is funded by the Baden-Württemberg Foundation in the program "Innovations for Adaptation to Climate Change".

## Overview

![parkli-dashbaord-app](https://github.com/os4os-repo/ParKli/blob/b02ae2953a32365ae824b7d84247df911727b4cc/images/parkli-dashboard.jpg)

The Parkli DashBoards are developed as a series of Pytho Dash pages that are containerised using Docker.The app is composed of the following Docker containers:

* **parkli-dashboard**: Containerised Python dash application. Provides a web server on port 80 under which the DashBoards can be reached. The image of this container must be built before deployment. The files of the actual dash app are mounted in the container via a host volume. Environmental data is stored separately in the postgres container. Credentials for the database connection are stored in the environment variable of the container.
* **parkli-postgres**: Database for data records from iNaturalist, GreenSpaceHack and EyeOnWater. Is initially fuelled with a backup and can be regularly updated using a job container. A standard image serves as the basis. The container stores persistent data in a host volume. Credentials for the database connection are stored in the environment variable of the container.
* **Networking**: The two containers are connected by their own Docker network called dashboard-net and can only communicate with each other. Every other participant must join this network in order to contact one of the containers. Therefore, the use of a reverse proxy is recommended, which hangs in dashboard-net on the one hand and has a host connection on the other. This allows incoming requests from outside to be forwarded through the reverse proxy to the dash app containers without having to connect them directly to the Internet.

## Installation

The deployment process consists of the following steps:

1. Preparing the config files
2. Build image 
3. Deploy the containers
4. Import of the initial data record

### 1. Preparing the config files

After downloading the repository, the env file must be renamed to ‘.env’ (without inverted commas) and the environment variables for the containers must be set in it. The values `POSTGRES_DBNAME`, `POSTGRES_USER` and `POSTGRES_PASS` must be adjusted. All other values can remain at their default values. The same must be done for the dbimport.sh script which is used to load the initial data record into the database.

### 2. Build image

The container for the Dash app must be created using the attached Dockerfile. To do this, change to the directory with the Dockerfile and use the command `docker build . -t parkli-dashboard/3 --no-cache` to build a new image. The name of the image can be changed, but must later match the information in the compose file. During the build process, the required additional software from the requirements.txt is installed on top of an existing Python image from the Docker Hub.

### 3. Deploy the containers

Once the image and environment variables have been prepared, the containers for the database and dashboard server can be started. To do this, execute the attached docker-compose.yml with the command `docker compose up -d` and wait until the stack is running. The output in the terminal should look like this:

![compose started](https://github.com/os4os-repo/ParKli/blob/c567074b57d0a6beb87f165d8526c2f78877ded4/images/compose_running.PNG)

After this step, a new route to the dashboard container can be created in the reverse proxy. To do this, take the host name of the dashboard container from the compose file as the destination and address it on port 80. If the traffic is routed correctly through the proxy, the dashboards are now visible in the browser.

### 4. Import of the initial data record

When the containers are started up for the first time, the environmental database does not contain any data records. The script `dbimport.sh` can be used to load an initial data set from [iNaturalist](https://www.inaturalist.org/) into the database. To do this, download the prepared data set from the [os4os datahub](https://datahub.openscience.eu/dataset/parkli-dash-database-dump) and store it in the host-volumes directory under dbdump, adjust the values of the parameters for HOST, USER and DATABASE in the script and execute the script. The import may take a few minutes.

## Installation ohne Reverse-Proxy

It is possible to operate the dashboards without a reverse proxy, but we advise against this in favour of security. Should this nevertheless be necessary, the installation process only differs in point 1. In this case, in addition to the environment variables, the `expose` must be replaced by `port` in the `parkli-dashboard` service in docker-compose.yml. This will connect port 80 of the web server in the container directly to the network stack of the host and thus to the (inter)net:

![compose port](https://github.com/os4os-repo/ParKli/blob/4b251be2c0fb85f72dd74e5a84d44da21f7f3d67/images/compose_port.PNG)

