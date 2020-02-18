# sqAPI
[![License MIT](https://img.shields.io/badge/license-MIT-blue.svg)](resources/docs/LICENCE 'MIT Licence')
[![](https://img.shields.io/docker/automated/mabruras/sqapi.svg)](https://hub.docker.com/r/mabruras/sqapi 'DockerHub')
[![](https://img.shields.io/docker/stars/mabruras/sqapi.svg)](https://hub.docker.com/r/mabruras/sqapi 'DockerHub')
[![](https://img.shields.io/docker/pulls/mabruras/sqapi.svg)](https://hub.docker.com/r/mabruras/sqapi 'DockerHub')


_Are you actually looking for the
[sqAPI Plugins Repository](https://github.com/mabruras/sqapi-plugins)?_

## About
sqAPI is a plugin based data aggregation system,
for subscribing to messages, query towards data- and metadata stores,
aggregate and expose data to the users.

Receiving a message will make the system fetch referred data and metadata,
calculate a hash digest and guess the mime type before proceeding.
Following an execution of all active plugins,
which accepts the guessed mime type, for custom data manipulation.
The manipulated data can be stored in a database or on disk if necessary -
dependent on the plugin implementations.

Each sqAPI plugin has its own area of responsibility, and will receive its own
copy of the queried data and metadata independent of each other.
The data being manipulated and/or reduced within the plugin,
can be stored in the sqAPIs local data storage.
The local storage type depends up on what data it's intended for.

When a user wants to search, or in other ways access the data,
they will do so through all of sqAPIs exposed API resources.


## Graphic illustrations
### Overview
The following figure gives an overview of sqAPIs position within a storage system.
As indicated within the figure,
there is intended to be deployed multiple sqAPI instances within the complete system.
A sqAPI instance could be deployed with a single, multiple or full set of plugins,
dependent on the environment setup and usage.

![sqAPI Overview](https://github.com/mabruras/sqapi/raw/master/resources/images/sqapi_overview.png)

### Details
The graphic below presents the flow and different components within the sqAPI solution.
The orange areas (_Processor Execution_ and _Resources_) are custom logic for each of the plugins.

![sqAPI Details](https://github.com/mabruras/sqapi/raw/master/resources/images/sqapi_details.png)


# Getting Started
## Quick Start
### Docker Compose
The Docker Compose solution will start several containers, based on the
[example system](https://github.com/mabruras/sqapi/blob/master/resources/docs/EXAMPLE_SYSTEM.md),
where you can follow a guide to set up a complete working solution.

With the Docker Compose file, each of the components are linked together in the same Docker Network.
It is built and started with the following
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
[their configuration](https://github.com/mabruras/sqapi/blob/master/resources/docs/CONFIGURATION.md#packages).
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

Eg. the data could be stored in a Swift storage,
while the metadata is stored in a Redis cache.
This requires that sqAPI is configured to reach those systems,
by selecting the correct configuration for sqAPI, and its plugins.

For example systems, take a look in
[resources / examples](https://github.com/mabruras/sqapi/blob/master/resources/examples)


### Docker
To load a set of plugins, it should be mounted as follows.
The example is taken with usage of the
[sqAPI Plugins Repository](https://github.com/mabruras/sqapi-plugins).
```bash
docker run -d \
  -p 5000:5000 \
  -v "${PWD}/../sqapi-plugins":/opt/mab/sqapi/plugin/plugins \
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
sqAPI has some default endpoints activated, read more about them in
[the endpoint section](https://github.com/mabruras/sqapi/blob/master/resources/docs/ENDPOINTS.md).


## Environment Variables
There are some environment variables, that could be set to overwrite specific default values.

| VARIABLE | EXAMPLE | DESCRIPTION | DEFAULT |
| :------- | :-----: | :---------- | :-----: |
| `WRK_DIR`| /opt/mab | Directory where sqAPI is located | current directory/`.` |
| `CFG_FILE`| /opt/mab/sqapi/resources/sqapi.yml | sqAPI main configuration file | `${WRK_DIR}/sqapi/resources/sqapi.yml` |
| `LOG_FILE`| /opt/mab/sqapi/resources/logging.conf | sqAPI log configuration file | `${WRK_DIR}/sqapi/resources/logging.conf` |
| `PLUGIN`| faces | Specifies a single plugin - disables all other | Empty/`None` |


# Contribution
There are multiple ways to contribute to sqAPI:
* Core logic
* Adding plugins
* Connector support

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
sqAPI supports a given set of connectors for external systems.
If you have a system not supported, feel free to report an issue or create a pull request.

Each of these external connection Topics should support as many external systems as possible.
The more, the merrier!

For detailed information, see
[the Connectors section](https://github.com/mabruras/sqapi/blob/master/resources/docs/CONNECTORS.md)

#### Connection Topics
* [Database](https://github.com/mabruras/sqapi/blob/master/resources/docs/CONNECTORS.md#database)
* [Data Store](https://github.com/mabruras/sqapi/blob/master/resources/docs/CONNECTORS.md#data-store)
* [Metadata Store](https://github.com/mabruras/sqapi/blob/master/resources/docs/CONNECTORS.md#metadata-store)
* [Message System](https://github.com/mabruras/sqapi/blob/master/resources/docs/CONNECTORS.md#message-system)
