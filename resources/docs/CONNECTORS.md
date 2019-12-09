# Connectors

## About
The connectors package is a collection of Topics (sub packages)
that sqAPI uses to connect towards external systems.

There are different type of external systems used in sqAPI,
where there is a Connector Topic for each one.

Within each Topic, there are different connector types for different system setups/technologies.

This README defines how to develop new connector _types_,
what is required and recommended when developing connectors for sqAPI.

The different types of connectors are all configurable and replaceable.
Within each of the Connector Topic, there are potentially multiple connector types.
Each type could have different configuration,
so make sure to read on before setting up the specific types for the different Topics.

#### Overview
The following external systems has its own Connector Topic,
located within the specific topics package.
(_Note: This setup is just an example stack_)

| External System | Topic | Package | Default Type |
| --------------- | ----- | ------- | ------------ |
| `Data Store` | `data` | `sqapi.connectors.data` | `disk` |
| `Metadata Store` | `meta` | `sqapi.connectors.meta` | `redis` |
| `Message System` | `listeners` | `sqapi.connectors.listeners` | `zeromq` |
| `Database` | `db` | `sqapi.connectors.db` | `postgres` |


## General
The general structure of the connectors, is the naming.
Each module is a `py`-file, where the name of the file represents the connector Topic type.

Eg.: 
_Swift_ is a _Connector Type_ of _Data Store_,
where the _Data Store_ is a _Connector Topic_.

This means that the Connector type (Swift) should be located as follows:
* Directory: `./sqapi/connectors/data/swift.py`
* Package: `sqapi.connectors.data.swift`

**Configuration:**
```yaml
data_store:
  type: 'swift'
  ... # Other configuration
```
Notice that the `type` field needs to match the name of the module,
or it will not be loaded in as a connector during runtime.


## Topics
Topics are the different set of Connector types, which defines an external system - independent of technology.
Within each Topic, there are multiple Connector types - which is technology specific.

This section lists all the Connector topics with complete set of their Connector types,
thus creating this the main documentation for the Connector topics and -types.

### Data Store
Data Store is a Topic for connecting towards a object storage solution.
The object storage could be everything from a disk storage, to a Amazon S3 bucket.

###### Structure
The Data Store types are not instantiated as objects,
but used directly as static modules.


#### Requirements
##### Functions
Only required function is `download_to_disk`.
See a more detailed example within one of
[the actual modules](https://github.com/mabruras/sqapi/blob/master/sqapi/connectors/data).
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
Metadata Store is a Topic for connectors querying towards where metadata is located,
typically the metadata will be stored as key-value pairs.
A Metadata Store could be a Redis instance, or other key-value based systems.

#### Structure
The Metadata Store types are not instantiated as objects,
but used directly as static modules.

#### Requirements
##### Functions
Only required function is `fetch_metadata`.
See a more detailed example within one of
[the actual modules](https://github.com/mabruras/sqapi/blob/master/sqapi/connectors/meta).
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


### Message System
Connector towards the Message System is responsible for subscribing to a
message broker, -bus or other message system connections,
for receiving messages for sqAPI to process.
This is the main trigger for loading data into sqAPI,
before each of the plugins custom logic is executed.

#### Structure
The Message System connector is an instantiated object,
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

After parsing the received message,
the resulting dictionary should be put in `sqapi.core.message.Message` and forwarded to `process_message`,
so the `ProcessManager` are able to process the message as intended.
Definition of `process_message` below.

##### Methods
###### Listeners
The following method is called upon from the main thread.
This means that each of the listeners needed within the connector,
should take care of its own retry/loop logic, threading etc.

```python

def start_listeners(self):
    pass
```

Notice that this is just the method called upon from the process manager,
to start the connectors listeners.
Within this method it's encouraged to start up each listener necessary.

Eg. it may be desirable in a RabbitMQ connector,
to start both an exchange listener as well as an queue listener.

###### Callback
Use the callback function when the listeners are fetching messages.

The callback sent to the `__init__` looks as follows,
where the `Message` is a wrapper object containing among others; a `body` attribute.
The `body` is a dictionary containing the message as key-values.
The Message object is to be sent along to the query section for both `data` and `metadata` connectors.
The `body` attribute will ending up as argument to the execute function in each plugin.

```python
from sqapi.core.message import Message

# Callback method located in the core.processor:
def process_message(self, message: Message):
    pass
```

#### Types
Regardless of the chosen type,
there should be included configuration
for which mime types each plugin supports.

The following configuration is example
of config used in a plugin configuration.
```yaml
msg_broker:
  # Supported Mime should be custom for each sqAPI Plugin,
  # not necessarily defined in the parent configuration
  supported_mime:
  - 'image/jpeg'
  - 'image/png'
  - 'image/gif'
```

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
    type:
      key: 'data_type'
      required: True
    data_location:
      key: 'data_location'
      required: True
    meta_location:
      key: 'meta_location'
      required: True
    uuid:
      key: 'uuid_ref'
      required: True
    metadata:
      key: 'metadata'
      required: False

  # Supported Mime should be custom for each sqAPI Plugin,
  # not necessarily defined in the parent configuration
  supported_mime:
  - 'image/jpeg'
  - 'image/png'
  - 'image/gif'
```

##### ZeroMQ
> ZeroMQ
>
> An open-source universal messaging library
- https://zeromq.org/

###### Configuration
```yaml
msg_broker:

  type: 'zeromq'
  host: '*'
  port: 5001
  retry_interval: 0
  process_delay: 0
  connection_type: bind
  socket_type: 7
  protocol: 'tcp'

  message_fields:
    type:
      key: 'data_type'
      required: True
    data_location:
      key: 'data_path'
      required: True
    meta_location:
      key: 'meta_path'
      required: True
    uuid:
      key: 'uuid'
      required: True
    metadata:
      key: 'metadata'
      required: False
```


### Database
The Database Connector is an interface implementation towards a specific type of database.
All connectors should be usable by each of the plugins, through one of two interfaces.
The interface used, is dependent on the Database Connector Type;
[_Relational storage_](#relational-storage) and [_Document storage_](#document-storage).

All document stores (eg. MongoDB, ElasticSearch, CouchDB, etc.) will share the same interface,
while all relational databases (eg. PostgreSQL, SQLite, MySQL, etc.) share another interface.
Each of the interfaces is described below, within their respective headings.

#### Structure
The sqAPI Core configuration can have a database connector defined,
that will be default for all plugins, as long as they support the database type.

The Database types are dependent on each plugin and their data structure.
It is possible to reuse the default connection from the sqAPI configuration,
where each plugin are able to overwrite if necessary.

The Database connector is an instantiated object, not used as a static module.


#### Instantiation
When the database connector is created (_using `__init__`-method_) it should
first create the database connection, test it, and store it within the connector.

By storing the database connection on the connector, the same connection will be reused
to avoid overhead of establishing and testing a connection on each query.
If the database connection is not thread safe, consider making a thread pool.

If needed; the initialization script should be run (usually just for relational
storage connectors). If the database connector cannot connect to the database
and retries is exceeded, the sqAPI should shut down -
at least not proceed with instantiating other connectors.

#### Class
The module must implement a class named `Database`,
regardless of being a relational DB or document storage.
```python
class Database:
    def __init__(self, config: dict):
        pass
```
The configuration sent to the init method will be a dictionary with
all `database` configuration defined in the yaml configuration file.

#### Relational Storage
The Relational Storage Database Connector type has the following requirements,
that must be implemented to suit the method calls from both sqAPI Core and -Plugins.

##### Methods
###### Initialization
The database connector needs an initialization method,
where all the setup is prepared, like creating tables, relations and views.
```python
from sqapi.core.message import Message

def initialize_database(self):
    pass
def initialize_message_table(self):
    pass
```

* The `initialize_database` should handle all preparation of the database,
* `initialize_message_table` is intended for setting up the
message table for the sqAPI core - if sqAPI is configured to use the connector.

###### Execution
There are two ways of executing queries against the database,
where there is either sent in a script file, containing a query string,
or the query string directly.
This lets each plugin potentially give the user the option to generate queries,
or keep predefined queries in scripts - might even be stored as templates.

The `**kwargs` will contain key-value pairs to replace the placeholders in the query string.
```python
def execute_script(self, script_path: str, **kwargs):
    pass
def execute_query(self, query: str, **kwargs):
    pass
```

##### Files
For Relational Database Connector types, there must be an initialization script,
which area of responsibility is to setup necessary adjustments of the database - like tables and views.
If the `init` fields is missing from the configuration, or not an existing file, the sqAPI will not start.

**Note**: _The `init` field should also be in place for Document Storage Database Connector type_

##### Types
###### PostgreSQL
> PostgreSQL is a powerful, open source object-relational database system with
over 30 years of active development that has earned it a strong reputation for reliability,
feature robustness, and performance.
- https://www.postgresql.org/

**Configuration**
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

#### Document Storage
The Document Storage Database Connector type has the following requirements,
that must be implemented to suit the method calls from both sqAPI Plugins.

##### Methods
###### Initialization
The database connector needs an initialization method,
where all the setup is prepared, like creating indices or other necessary setup.
```python
def initialize_database(self):
    pass
```

###### Execution
There are two ways of interacting with the storage solution,
where one is to insert a new document, while the other is to retrieve the stored document.
```python
def create_document(self, area: str, body: dict, kind: str):
    pass
def fetch_document(self, area: str, body: dict, query_clause):
    pass
```
* The `area` parameter indicates where the document is to be stored,
which could be an index, collection or other storage groupings.
* `body` being the actual document to store, or the content of the query towards the storage.
* If needed, the `kind` of document could be defined - specifying where within the `area` the document is to be stored.
* By using `query_clause` the connector can switch between different ways of query the stored data.

##### Types
###### Elasticsearch
> Elasticsearch is a distributed, RESTful search and analytics engine capable of
addressing a growing number of use cases. As the heart of the Elastic Stack,
it centrally stores your data so you can discover the expected and uncover the unexpected.
- https://www.elastic.co/products/elastic-stack

**Configuration**
```yaml

database:
  type: 'elasticsearch'
  kwargs:
    # sniff_on_start: true
    # sniff_on_connection_fail: true
    # sniff_timeout: 10
    # sniffer_timeout: 60
  connection:
  - name: 'elasticsearch'
    port: '9200'
    user: 'elasticuser'
    host: 'es'
    password: 'elasticpass'
    timeout: 2
```

The `kwargs` dictionary will be sent to the constructor of the Elasticsearch client.
Please take a look at the [Elasticsearch API documentation](https://elasticsearch-py.readthedocs.io/en/master/)
for more concrete values that could be defined.

The `connection` field is a list of connections, where each running instance of the cluster should be defined,
unless using the `sniff_on_start` keyword in the `kwargs` dictionary.


# Contribution
When contributing it's easy to forget about the standards, requirements and other stuff.
Be sure to read up on the Connector you want to extend, add, or maintain - before submitting a pull request.
