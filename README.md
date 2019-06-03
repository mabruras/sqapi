# sqAPI System

## About
*sqAPI System* is a complete system for receive files and being able to
make query towards aggregated data of these files.

The system will receive files, store them in a object database (or disk in this _PoC_),
the metadata of the files are stored in a key-value store,
and a notification is published on the message broker.

When a message is received, each *sqAPI* subscribed to that specific queue,
will query relevant files from the key-value store and the object database.
Each *sqAPI* has its own responsibility area, and will query data and metadata
independent of each other. The data aggregated within the *sqAPI*, will be stored in
the *sqAPI*s local data storage, which kind depends up on what data it's intended for.

When a user wants to search, aggregate or in other ways access the data,
they will through the web ui access all necessary *sqAPI*s exposed APIs.


# Components
This PoC consist of a set of components,
all intended to populate a central storage unit,
then execute specific logic on incoming data and expose the new data set to the users.

The components are represented by specific technologies in this PoC,
but should be possible to change with other similar alternatives.

| Component | Technology | Description |
| --------- | ---------- | ----------- |
| `Data Loader` | `NiFi` | Loading data into `Data Store`, `Metadata Store` and `Message Broker` |
| `Data Store` | `Xubuntu file system` | Keeping original incoming files |
| `Metadata Store` | `Redis` | Holding metadata with ID reference to `Data Store` location |
| `Message Broker` | `RabbitMQ` | Publishes messages to each active `sqAPI`-instance |
| `Graphical User Interface` | `ReactJS` | Representation of aggregated data within one or multiple `sqAPI`'s |
| `sqAPI` | `Python` | System for execute queries on subscribed data, based on specific subset, to make it available |
| `sqAPI Storage` | `PostgreSQL` | Local storage for each `sqAPI`, keeps record of all messages and aggregated data |
| `-` | `-` | `-` |


## Data Loader
As Data Loader, NiFi is used to move files on the disk, into Redis, and the message queue.

* Store file to `Data Store` (_on disk_)
* Store metadata in `Metadata Store` (_Redis_)
* Notify `Message Broker` (_RabbitMQ_) of received file
  * Message should contain `Metadata Store`- and `Data Store`-references

### Preparation
#### IO directories
After NiFi has started,
the following folders should be created to
`docker exec -u 0 -it nifi bash -c "mkdir -p /io/{input,output}/ && chown nifi:nifi -R /io"`

#### Flow
When uploading a file into NiFi, the *Main*-flow is executed.

After *Main*, the flow is forked into three:
*Store File*, *Store Metadata*, *Publish Message*

![NiFi Flow](./nifi-flow.png)


##### Main
* `GetFile`: Picks up files for processing
  * `Input Directory`: `/io/input`
  * Load custom files with `docker cp <file> nifi:/io/input/`
* `IdentifyMimeType`: Sets `mime.type` as attribute
* `UpdateAttribute`: Creates attributes for sqAPI message fields
  * `data_type`: `${mime.type}`
  * `data_location`: `/io/output/${uuid}`
  * `meta_location`: `redis/${uuid}`
  * `uuid_ref`: `${uuid}`
  * `filename`: `${uuid}`

##### Store file
* `PutFile`: Stores files on disk
  * `Directory`: `/io/output`

##### Store metadata
* `AttributesToJSON`: Extracts metadata from file, and creates new FlowFile with attributes as JSON content
  * `Destination`: `flowfile-content`
* `PutDistributedMapCache`: Inserts attributes (metadata) as JSON, into Redis
  * `Distributed Cache Service`: `RedisDistributedMapCacheClientService`
    * `Redis Connection Pool`: `RedisConnectionPoolService`
      * `Connection String`: `redis:6379`

##### Publish Message
* `AttributesToJSON`: Extracts metadata from file, and creates new FlowFile with attributes as JSON content
  * `Destination`: `flowfile-content`
  * `Attributes List`: `data_type, data_location, meta_location, uuid_ref`
* `PublishAMQP`: Publish messages to RabbitMQ
  * `Exchange Name`: `x_sqapi`
  * `Routing Key`: `q_sqapi`
  * `Host Name`: `mq`


## Data Store
For data store in this PoC, only local disk are used as storage for loaded files.
Next step would probably be to use AWS S3 as object storage.


## Metadata Store
Redis is used for Metadata Store, to keep metadata about the loaded files.

### PoC
Within the [Redis directory](./redis) it exists two scripts,
one for writing to Redis, and one to read out based on input arguments.

### Preparation
#### Prerequisites
* Using _redis_ python client for communication with the Redis instance
  * `pip3 install redis --upgrade`


## Message Broker
RabbitMQ is used as message broker, to publish messages.
* Receive messages from `Data Loader`
* Publish messages to all subscribed `sqAPI`-instances

### PoC
Within the [RabbitMQ directory](./rabbitmq) there is created four files:
* [queue_producer](rabbitmq/queue_producer.py): publish single messages
* [queue_consumer](rabbitmq/queue_consumer.py): fetch messages from single queue
* [exchange_producer](rabbitmq/exchange_producer.py): publish messages to all queues
* [exchange_consumer](rabbitmq/exchange_consumer.py): fetch messages from custom queue

These files are only used as a PoC for this system.

### Preparation
#### Prerequisites
* Using _Pika_ python client for AMQP protocol
  * `pip3 install pika --upgrade`


## Graphical User Interface
`Curl` will be used until a Web-frontend solution is in place.
Planned GUI will be developed in ReactJS.


## sqAPI
_Subscription, Query, API_ is a component intended to subscribe to the `Message Broker`,
query data from `Data Store` and metadata from `Metadata Store`.

New data from the queue will trigger a query and aggregation of the newly incoming data.
All aggregated data will be stored in a *sqAPI* specific storage solution (`sqAPI Storage`),
dependent on the intentions of the current *sqAPI*.

When a user wants to access the aggregated data, they will connect to the API directly or through the GUI,
and the *sqAPI* will perform necessary searches in its local database,
and possibly queries towards `Data Store` and `Metadata Store` for fetching necessary supplements to return to the user.

### PoC
The [sqAPI Proof of Concept](./sqapi) will receive data from `Message Broker`,
store references for `Data Store`- and `Metadata Store`, generated _timestamp_,
_file size_ generated of queried data from `Data Store`, _filename_ fetched from `Metadata Store`,
and _mime type_ in `sqAPI Storage` as aggregated data.
The aggregated data will be made available for search on timestamp, file size, filename and mime type.

The `Metadata Store` and `Data Store` should be queried when endpoints for fetching them is triggered.

#### Stages
* Register subscription to RabbitMQ
* Query for metadata and file, on message received
* Aggregate data
* Store aggregated data in local storage (PostgreSQL)
* Perform necessary searches in local database
* Fetch data/metadata based on local results
* Return data/metadata to used based on request


## sqAPI Storage
PostgreSQL is used as sqAPI Storage, to store all data aggregations locally, from queried data.

### Preparation
Independent of storage type, there should be a setup function made available,
to create necessary structures to fill the following needs:
* Failed messages
  * Messages failed processing should be stored locally
  * Messages failed in query step, should be retried after a defined amount of time
* Modified data
  * Aggregated data should be stored locally for searches and sqAPI logic


# Getting Started

## Docker Compose
The Docker Compose solution will create a container for each active component in the [sqAPI PoC](./sqapi).
Each of the components are linked together in the same Docker Network.

The Docker Compose solution is built and started with the following
```bash
docker-compose build
docker-compose up -d
```

## sqAPI
This PoC is based on a file system as origin to the files, a Redis instance as origin for the metadata,
a RabbitMQ for message bus, and PostgreSQL to store the processed data.

### Test sqAPI PoC
Use the following to start the sqAPI PoC, with both subscription/query and API, and insert test data.
```bash
# Start Redis, RabbitMQ and PostgreSQL
docker run -d -p 6379:6379 redis:latest
docker run -d -p 5672:5672 rabbitmq:latest
docker run -d -p 5432:5432 postgres

# Start sqAPI
./sqapi/start.py

# Produce test data
./data_producer.py
```


### sq & API
`sqAPI` can be started as two separate services,
where one is responsible for loading the data,
while the other is responsible to serve the API.

This will let the Loader being able to load data even though the API is down,
as well as users are able to access data when the loader is down.

#### sqAPI Loader
```bash
python3 sqapi/start.py loader
```

#### sqAPI API
```bash
python3 sqapi/start.py api
```
