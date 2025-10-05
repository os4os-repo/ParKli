# Overview

The buoys continuously send measured values to TheThingsNetwork (TTN) via the LoRa protocol. Among other things, the TTN converts the raw data from the sensors from individual bit and byte patterns into human-readable formats in so-called payload formatters (PF). The output of a PF is not stored by the TTN in a usable form; historical values can only be viewed for a short time via the processing log. In order to store the measurement data from the sensors in a structured manner over longer periods of time and to carry out various actions such as visualisation and manipulation, we transfer the data to a self-hosted server stack.

The aim was for the designed system (called IoT_Stack) to provide the basic functions of data processing, storage and visualisation and for the data exchange between TTN and IoT_Stack to use standardised interfaces. In order to give non-IT people the opportunity to use the functions of the IoT stack, we have focussed in particular on integrating components with a low-code/no-code development approach. All components are virtualised using container technology in order to keep the infrastructure costs for providing the IoT_Stack as low as possible.

This requirement has resulted in the system shown below. The IoT stack uses Docker as the container technology. Docker is one of the most widely used tools in this technology and is therefore well documented.

![IoT_Stack](https://github.com/os4os-repo/ParKli/blob/4fd0e3cbf333564c51f16320ce9b19cf4feb900e/IoT_Stack/IoT_Stack.PNG)

## Node-RED

We rely on the low-code development environment Node-RED for data processing. Node-RED allows us to build interfaces to the TTN using MQTT PubSub and an HTTP endpoint. The received data can then be processed in Node-RED in so-called flows. A flow allows a user/developer to build processing chains within a web-based graphical editor using predefined function blocks to transform an input (e.g. measured value from TTN) in several steps and then save it again in the database of the IoT_Stack via a function block. 
Basic settings for Node-RED are contained in a configuration file called settings.js. For the stack, this file has been extended to read inputs from the Docker environment variables of the environment file. The settings.js must therefore be stored in a host directory to start the container.

## InfluxDB

The stack contains a container with an InfluxDB database for storing the measured values. InfluxDB is a time series database optimised to manage measured values with a temporal reference. InfluxDB can be controlled via the command line or via a WebGUI. Reading and writing to/from InfluxDB can be done via a predefined function module (node) within Node-RED.

## InfluxDB Backup

It is possible to have the Influx database backed up automatically. To do this, the attached shell script must be executed nightly via root crontab. The script generates a dump of the entire database via the Influx DBMS and stores it in a host directory. The backup is zipped and encrypted from this host directory. In parallel a Log-File is written to /var/log. You have to adapt the settings in the shell script!

## Grafana

In order to create graphics such as pie charts, gauges, xy charts,... Grafana is included in the stack. Grafana is a widely used visualisation tool that can be accessed by the user as a WebGUI and can integrate various databases (including InfluxDB). Grafana offers the possibility to create your own diagrams consisting of visualisation + data query via an editor. Knowledge of query languages such as SQL is not absolutely necessary. 

# System requirements

The IoT stack was tested with the following tools and versions:

* Docker - version 27.2.1
* Docker Compose - version 2.29.2
* node-red-admin - version 4.0.1
* Node-RED Docker Image - version 4.0.3
* InfluxDB Docker Image - version 2.7.10
* Grafana Docker Image - version 8.3.3

The stack was developed and tested under Ubuntu 22.04.5 LTS. For the IoT stack, the server should be equipped with at least 2vCPUs, 4GB RAM and 70GB hard drive space. These values may vary depending on the workload.

All three containers persist their data in host directories. This directory structure must be created before the containers are started, according to the volume specifications in the docker-compose.yml file.
This would be:

* iotstack
  * data
    * grafana
    * influxdb
    * nodered
      * settings.js 
  * docker-compose.yaml

