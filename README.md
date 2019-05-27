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

## NiFi
NiFi is used to move files into the message queue.

* Store file on disk
* Store metadata in Redis
* Notify RabbitMQ of received file
  * Message should contain Redis ref. and path to stored file

### Tools
* `GenerateFlowFile`: Creates dummy files
* `PutFile`: Stores files on disk
* `AttributesToJSON`: Extracts metadata from file, and creates new FlowFile with attributes as JSON content
* `PutDistributedMapCache`: Store metadata in Redis
* `PublishAMQP`: Publish messages to RabbitMQ

## Redis
Redis is used for key-value store/map cache,
to keep metadata about files uploaded.

### Tools
Within the [Redis directory](./redis) theres exists two scripts,
one for writing to Redis, and one to read out based on input arguments.

#### Prerequisites
* Using _redis_ python client for communication with the Redis instance
  * `pip3 install redis --upgrade`


## RabbitMQ
RabbitMQ is used as message broker.
* Receive messages from NiFi
* Publish these messages on the queue

### Tools
Within the [RabbitMQ directory](./rabbitmq) there is created four files:
* [queue_producer](rabbitmq/queue_producer.py): publish single messages
* [queue_consumer](rabbitmq/queue_consumer.py): fetch messages from single queue
* [exchange_producer](rabbitmq/exchange_producer.py): publish messages to all queues
* [exchange_consumer](rabbitmq/exchange_consumer.py): fetch messages from custom queue

These files are only used as a PoC for this system.

#### Prerequisites
* Using _Pika_ python client for AMQP protocol
  * `pip3 install pika --upgrade`


## sqAPI
_Subscription, Query, API_ is a component intended to subscribe to the message broker,
query data from disk/storage place and metadata from key-value store/map cache.

New data from the queue will trigger a query and aggregation of the newly incomming data.
All aggregated data will be stored in a *sqAPI* specific storage solution,
dependent on the current *sqAPI* intentions.

When a used wants to access the *sqAPI*s data, they will connect to the API and the *sqAPI*
will perform necessary searches and queries towards its local database,
or towards the storage for fetching data and metadata to return to the user.

### Incomming data
* Register subscription to RabbitMQ
* Query for file data when RaMQ notifies
* Query for files on disk when RaMQ notifies
* Store data in local storage (ES)

### Incomming user request
* Perform necessary searches in local database
* Fetch data/metadata based on local results
* Return data/metadata to used based on request

## Storage
PostgreSQL is used to keep the data for the current PoC

## User Interface
Curl/Kibana

