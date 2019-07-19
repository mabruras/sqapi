# sqAPI
[![License MIT](https://img.shields.io/badge/license-MIT-blue.svg)](resources/docs/LICENCE 'MIT Licence')
[![](https://img.shields.io/docker/automated/mabruras/sqapi.svg)](https://hub.docker.com/r/mabruras/sqapi 'DockerHub')
[![](https://img.shields.io/docker/stars/mabruras/sqapi.svg)](https://hub.docker.com/r/mabruras/sqapi 'DockerHub')
[![](https://img.shields.io/docker/pulls/mabruras/sqapi.svg)](https://hub.docker.com/r/mabruras/sqapi 'DockerHub')


_Are you actually looking for the
[sqAPI Plugins Repository](https://github.com/mabruras/sqapi-plugins)?_

## About
*sqAPI* is a plugin based system for subscribing to messages,
query towards data- and metadata stores,
aggregate and expose data to the users.

Receiving a message will make the system fetch referred data and metadata,
and execute all active plugins for custom data aggregation.
The aggregated data will be stored in a local database, and on disk if necessary.

Each *sqAPI* plugin has its own area of responsibility, and will query data and metadata
independent of each other. The data aggregated within the plugin, will be stored in
the *sqAPI*s local data storage.
The storage type depends up on what data it's intended for.

When a user wants to search or in other ways access the data,
they will through all necessary *sqAPI*s exposed APIs.

## Graphic illustrations
### Overview
This figure gives an overview of *sqAPI*s position within a storage system.
As indicated within the figure,
there is intended to deploy multiple *sqAPI* instances within the complete system.
Each deployed sqAPI will have its own area of responsibility (_active plugin_).

![sqAPI Overview](resources/images/sqapi_overview.png)

### Details
The graphic below presents the flow and different components within the sqAPI solution.
The orange areas (_Processor Execution_ and _Resources_) are custom logic for each of the plugins.

![sqAPI Details](resources/images/sqapi_details.png)


# Getting Started
## Quick Start
### Docker Compose
The Docker Compose solution will start several containers,
based on the [example system](resources/docs/EXAMPLE_SYSTEM.md),
where you can follow a guide to set up a complete working solution.

With this Docker Compose file,
each of the components are linked together in the same Docker Network.

The Docker Compose solution is built and started with the following
```bash
docker-compose build
docker-compose up -d
```

## sqAPI
### Packages
It is important to note that the [sqAPI plugins](https://github.com/mabruras/sqapi-plugins)
could be based on logic which require custom dependencies, not covered in the original
[sqAPI Docker image](https://hub.docker.com/r/mabruras/sqapi).

#### PIP Packages
Each plugin are able to install their own PIP packages, by just listing them in
[their configuration](resources/docs/CONFIGURATION.md#packages).
The packages will be installed runtime, and might drastically increase the first time startup.

#### APT Packages and custom installations
In cases where there are dependencies towards either APT packages, or other "external installations",
there should be a Dockerfile within the plugin for the necessary installations.

#### Package Solution
PIP packages could be installed runtime, but increases startup time and thus not recommended.
External packages/installations needs to be installed/prepared up front.

When using Docker, the installations should be done by creating your own image from
`mabruras/sqapi:latest`, where all packages (both APT, PIP and others) gets installed.
This will keep the startup time low, but increase the image size.

If you run sqAPI outside Docker, you should prepare your environment with all
necessary installations, based on the documentation of the plugins you want to use.

### Prerequisites
sqAPI is dependent on receiving messages,
and being able to fetch elements from external systems.
Use the following to start the external systems;
a Redis as metadata store, a RabbitMQ as message broker,
a PostgreSQL as the internal database and sqAPI itself.

In this example, the data store is represented by `disk`
at the host running the solution.

Use [data producer](resources/test/data_producer.py) to insert test data.
```bash
# Start Redis, RabbitMQ and PostgreSQL
docker run -d -p 6379:6379 redis:latest
docker run -d -p 5672:5672 rabbitmq:latest
docker run -d -p 5432:5432 postgres

# Start sqAPI
./start.py

# Produce test data
./resources/data_producer.py
```

### Docker
To load a set of plugins, it should be mounted as follows.
The example is taken with usage of the
[sqAPI Plugins Repository](https://github.com/mabruras/sqapi-plugins).
```bash
docker run -d \
  -p 5000:5000 \
  -v "${PWD}/../sqapi-plugins":/opt/sqapi/sqapi/plugins \
  mabruras/sqapi
```


## sq & API
`sqAPI` can be started as two separate services, where one is responsible
for loading the data, while the other is responsible to serve the API.

This will let the Loader being able to load data even though the API is down,
as well as users are able to access data when the loader is down.

### sqAPI Loader
Each plugin has its own logic for aggregating data,
as soon as it's received by the custom execution.

To only start the sqAPI loader:
```bash
python3 start.py loader
```

### sqAPI API
The API part of a plugin contains all of its resources,
to let the end users access the aggregated data.

To only start the sqAPI API:
```bash
python3 start.py api
```

### Internal API
*sqAPI* has some default endpoints activated, read more about
them in [the endpoint section](resources/docs/ENDPOINTS.md).


## Environment Variables
There are some environment variables, that could be set to overwrite specific default values.

| VARIABLE | EXAMPLE | DESCRIPTION | DEFAULT |
| :------- | :-----: | :---------- | :-----: |
| `WRK_DIR`| /opt/sqapi | Directory where sqAPI is located | current directory/`.` |
| `CFG_FILE`| /opt/sqapi/conf/sqapi.yml | sqAPI main configuration file | `${WRK_DIR}/conf/sqapi.yml` |
| `LOG_FILE`| /opt/sqapi/conf/logging.conf | sqAPI log configuration file | `${WRK_DIR}/conf/logging.conf` |
| `PLUGIN`| faces | Specifies a single plugin - disables all other | Empty/`None` |


# Contribution
There are multiple ways to contribute to *sqAPI*:
* Core logic
* Adding plugins
* Increased support

## Core
The core functionality should always be improved,
so if you find a bug, an issue or some improvement potential -
feel free to commit a fix or a feature.

## Plugins
sqAPI is based on having all of its business logic implemented as plugins.

To contribute with a new plugin, please see
[the plugin repository](https://github.com/mabruras/sqapi-plugins/blob/master/README.md)
for information regarding structure, requirements and implementation details.

## Connectors
*sqAPI* supports a given set of connectors for external systems.
If you have a system not supported, feel free to report an issue or create a pull request.

Each of these external connection Topics should support as many external systems as possible.
The more, the merrier!

For detailed information, see [the Connectors section](resources/docs/CONNECTORS.md)

#### Connection Topics
* [Database](resources/docs/CONNECTORS.md#database)
* [Data Store](resources/docs/CONNECTORS.md#data-store)
* [Metadata Store](resources/docs/CONNECTORS.md#metadata-store)
* [Message Broker](resources/docs/CONNECTORS.md#message-broker)
