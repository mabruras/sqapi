# Connectors

## About
The connectors package is a collection of Topics (sub packages)
that sqAPI uses to connect towards external systems.

There are different type of external systems used in sqAPI,
where there is a Connector Topic for each one.

Within each Topic, there are different connector Types for different system setups/technologies.

This README defines how to develop new connector Types,
what is required and recommended when developing connectors for sqAPI.

The different Types of connectors are all configurable and replaceable.
Within each of the Connector Topic, there are potentially multiple connector types.
Each type could have different configuration,
so make sure to read on before setting up the specific types for the different Topics.

#### Overview
| External System | Topic | Package | Default Type |
| --------------- | ----- | ------- | ------------ |
| `Data Store` | `data` | `sqapi.connectors.data` | `disk` |
| `Metadata Store` | `meta` | `sqapi.connectors.meta` | `redis` |
| `Message Broker` | `listeners` | `sqapi.connectors.listeners` | `rabbitmq` |
| `Database` | `db` | `sqapi.connectors.db` | `postgres` |


## General
The general structure of the connectors, is the naming.
Each module is a `py`-file, where the name of the file represents the connector topic type.

Eg.: 
_Swift_ is a _Connector Type_ of _Data Store_,
where the _Data Store_ is a _Connector Topic_.

This means that the Connector Type (Swift) should be located as follows:
* Directory: `./sqapi/connectors/data/swift.py`
* Package: `sqapi.connectors.data.swift`
* x: `y`
* Configuration:
```yaml
data_store:
  type: 'swift'
  ... # Other configuration
```
Notice that the `type` field needs to match the module name,
or else it will not be loaded in as a connector runtime.


## Topics
Topics are the different set of Connector Types, which defines an external system - independent of technology.
Within each Topic, there are multiple Connector Types - which is technology dependent.

### Data Store
Data Store is a Topic for connecting towards a object storage solution.
The object storage could be everything from a disk storage, to a Amazon S3 bucket.

###### Structure
The Data Store Types are not instantiated as objects,
but used directly as static modules.


#### Requirements
##### Functions
Only required function is `download_to_disk`.
See a more detailed example within one of
[the actual modules](../../sqapi/connectors/data).
```python
import os

def download_to_disk(config, object_ref):
    ## 1. Connect to the object storage
    ## 2. Get the object wanted
    ## 3. Store the object as a temporary file
    ## 4. Return the path of the temporary file
    return os.sep.join(['my', 'path', 'to', object_ref])
```

Note that the config input contains all configuration defined in `data_store`,
so it is possible to use type specific connector configuration.

#### Types
##### Disk
Local disk, referenced by path to the host where sqAPI is deployed.
Typically used for testing, or in cases where there is no object storage available.

###### Configuration
Disk does not need any other configuration than the `type` field.
```yaml
data_store:
  type: 'disk'
```

##### Swift
> The OpenStack Object Store project, known as Swift,
offers cloud storage software so that you can store and retrieve lots of data with a simple API.
- https://wiki.openstack.org/wiki/Swift

###### Configuration
Credentials and host configurations is the bare minimum for connecting towards Swift.
More features might be necessary, and implemented when they are.

```yaml
data_store:
  type: 'swift'
  access_key_id: 'group:user'
  secret_access_key: 'myS3cr3tK3y'
  auth_url: 'http://localhost:8080/auth/v1.0'
  containers:
  - 'testcontainer'
  auth_version: '3'
  insecure: 'true'
  os_options:
    user_domain_name: 'Default'
    project_domain_name: 'Default'
    project_name: 'Default'
```

When accessing data, the connector will search for available containers
and try to retrieve the object from it, until it finds it.
This is possible to avoid by specify a specific a list of containers in the configuration.


### Metadata Store
Metadata Store is a Topic for connectors towards where metadata is stored,
usually stored as key-value pairs.
A Metadata Store could be a Redis instance, or other key-value based systems.

#### Structure
The Metadata Store Types are not instantiated as objects,
but used directly as static modules.

#### Requirements
##### Functions
Only required function is `fetch_metadata`.
See a more detailed example within one of
[the actual modules](../../sqapi/connectors/meta).
```python
def fetch_metadata(config, reference):
    ## 1. Connect to the metadata store
    ## 2. Get the metadata wanted
    ## 3. Convert results to dictionary
    ## 4. Return metadata as key-values in a dictionary
    return dict()
```

Note that the config input contains all configuration defined in `meta_store`,
so it is possible to use type specific connector configuration.

#### Types
##### Redis
> Redis is an open source (BSD licensed), in-memory data structure store,
used as a database, cache and message broker.
- https://redis.io/

###### Configuration
Currently no credentials are supported,
but this should be implemented really soon.
```yaml
meta_store:
  type: 'redis'
  host: 'localhost'
  port: 6379
```


### Message Broker
Connector towards the Message Broker is responsible for subscribing
to a message broker for receiving messages to each plugin to process.
This is the main trigger for loading data into sqAPI,
and execute the plugins custom logic.

#### Structure
The Message Broker connector is an instantiated object,
not used as a static module.

#### Requirements
##### Class
The module must implement a class: `Listener`, like follows.
```python
class Listener:
    def __init__(self, config: dict, process_message):
        pass
```
The configuration sent to the init method will contain
the dictionary with all `msg_broker` configuration defined.

After parsing the message received,
the result dictionary should be forwarded to `process_message`,
so the `core.processor` are able to process the message as intended.

##### Methods
###### Listeners
These methods are ran once from a separate thread.
This means that each of the methods should take care of its own retry/loop logic.

```python
def listen_exchange(self, callback):
    pass

def listen_queue(self, callback, routing_key=None):
    pass
```
The callback sent in looks as follows,
where the `body` is a dictionary containing the body as key-values.
This dictionary is to be sent along to the query section for both
`data` and `metadata` connectors, ending up as argument in each plugin.

```python
# Callback method located in the core.processor:
def process_message(self, body: dict):
    pass
```

#### Types
##### RabbitMQ
> RabbitMQ is the most widely deployed open source message broker.
- https://www.rabbitmq.com/

###### Configuration
```yaml
msg_broker:
  type: 'rabbitmq'
  host: 'localhost'
  port: 5672

  routing_key: 'q_sqapi'
  exchange_name: 'x_sqapi'
  exchange_type: 'fanout'
  process_delay: 5

  message_fields:
  - 'data_type'
  - 'data_location'
  - 'meta_location'
  - 'uuid_ref'

  # Supported Mime should be custom for each sqAPI Plugin,
  # not necessarily defined in the parent configuration
  supported_mime:
  - 'image/jpeg'
  - 'image/png'
  - 'image/gif'
```


### Database
The Database Types are dependent on each plugin and their data structure.
It is possible to create a default connection for the sqAPI instance,
where each plugin are able to overwrite if necessary, but this is not recommended.

#### Structure
The Database connector is an instantiated object,
not used as a static module.

When instantiated it should try the connection and run the initialization script, if needed.
If the database connector cannot connect to the database,
the sqAPI should shut down - at least not proceed with instantiating other connectors.

#### Requirements
##### Class
The module must implement a class: `Database`, like follows.
```python
class Database:
    def __init__(self, config: dict):
        pass
```
The configuration sent to the init method will contain
the dictionary with all `database` configuration defined.

##### Methods
###### Init
The database connector needs a initialization method,
where all the setup is prepared and tested.
```python
def initialize_database(self):
    pass
```

###### Execution
There are two ways of executing queries against the database,
where there is either sent in a script file, containing a query string,
or the query string directly.

The `**kwargs` will contain key-value pairs to replace the placeholders in the query string.
```python
def execute_script(self, script_path: str, **kwargs):
    pass
def execute_query(self, query: str, **kwargs):
    pass
```

###### Status Updates
When receiving a message, it is important that the processors for
all the plugins are able to register their status of processing.
The `core.processor` will call upon this method as a small log,
in case something breaks while processing the message.
```python
def update_message(self, message: dict, status: str, info: str = None):
    pass
```

##### Files
For each of the Database Connector Types, there must be an initialization script,
which area of responsibility is to setup necessary adjustments of the database.
If the `init` fields is missing from the configuration,
or not an existing file, the sqAPI will not start.

#### Types
##### PostgreSQL
> PostgreSQL is a powerful, open source object-relational database system with
over 30 years of active development that has earned it a strong reputation for reliability,
feature robustness, and performance.
- https://www.postgresql.org/

###### Configuration
```yaml
database:
  type: 'postgres'
  init: 'scripts/init.sql'
  connection:
    name: 'postgres'
    port: '5432'
    user: 'postgres'
    host: 'localhost'
    password: 'postgres'
    timeout: 2
```


# Contribution
When contributing it's easy to forget about the standards, requirements and other stuff.
Be sure to read up on the Connector you want to extend, add, or maintain - before submitting a pull request.
