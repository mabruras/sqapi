# NiFi - Redis - RabbitMQ
Example setup explaining how sqAPI can be used with RabbitMQ,
Redis as metadata store and a NiFi instance to load all data into sqAPI

**Note: This is a guide to setup your own example system!**

## Components

| Component | Technology | Description |
| --------- | ---------- | ----------- |
| `Data Loader` | `NiFi` | Loading data into `Data Store`, `Metadata Store` and `Message Broker` |
| `Data Store` | `File System` | Data located on disk |
| `Metadata Store` | `Redis` | Holding metadata with ID reference to `Data Store` location |
| `Message System` | `RabbitMQ` | Publishes messages to each active `sqAPI`-instance |
| `sqAPI` | `Python` | System for executing queries based on a subscription, fetch, aggregate and expose data |
| `sqAPI Storage` | `PostgreSQL` | Local storage for each `sqAPI`, keeps record of all messages and aggregated data |


## Data Loader
As Data Loader, NiFi is used to move files onto the disk, into Redis, and notify the message broker.

* Pick up incoming files
* Store file to `Data Store` (_on disk_)
* Store metadata in `Metadata Store` (_Redis_)
* Notify `Message Broker` (_RabbitMQ_) of received file
  * Message should contain `Metadata Store`- and `Data Store`-references, as well as data type

### Preparation
#### IO directories
After NiFi has started, the following folders should be created and given permissions:
`docker exec -u 0 -it nifi bash -c "mkdir -p /io/{input,output}/ && chown nifi:nifi -R /io"`

#### Flow
When uploading a file into NiFi, the *Main*-flow is executed.

After *Main*, the flow is forked into three:
*Store File*, *Store Metadata*, *Publish Message*

![NiFi Flow](https://github.com/mabruras/sqapi/raw/master/resources/examples/nifi_redis_rabbit/nifi-flow.png)


##### Main
* `GetFile`: Picks up files for processing
  * `Input Directory`: `/io/input`
  * Load custom files with `docker cp <file> nifi:/io/input/`
* `IdentifyMimeType`: Sets `mime.type` as attribute
* `UpdateAttribute`: Creates attributes for sqAPI message fields

###### UpdateAttribute properties
|     |     |     |
| --- | --- | --- |
| `data_type` | `${mime.type}` | Used to define type of data sent to sqAPI |
| `data_location` | `/io/output/${uuid}` | Reference in the data store system |
| `meta_location` | `${uuid}` | Reference in the metadata store system |
| `uuid_ref` | `${uuid}` | Unique ID, kept in `uuid_ref` due to NiFi fork creates new UUIDs |
| `filename` | `${uuid}` | Overwritten to avoid collision in `PutFile`-processor |

##### Store file
* `PutFile`: Stores files on disk
  * `Directory`: `/io/output`

##### Store metadata
* `AttributesToJSON`: Extracts metadata from file, and creates new FlowFile with attributes as JSON content
  * `Destination`: `flowfile-content`
* `PutDistributedMapCache`: Inserts attributes (metadata) as JSON, into Redis
  * `Cache Entry Identifier`: `${uuid_ref}`
  * `Distributed Cache Service`: `RedisDistributedMapCacheClientService`
    * `Redis Connection Pool`: `RedisConnectionPoolService`

###### Redis Connection Pool properties
|     |     |     |
| --- | --- | --- |
| `Connection String` | `redis:6379` | Host and port number for running Redis instance |

##### Publish Message
* `AttributesToJSON`: Extracts metadata from file, and creates new FlowFile with attributes as JSON content
  * `Destination`: `flowfile-content`
  * `Attributes List`: `data_type, data_location, meta_location, uuid_ref`
* `PublishAMQP`: Publish messages to RabbitMQ

###### PublishAMQP properties
|     |     |     |
| --- | --- | --- |
| `Exchange Name` | `x_sqapi` | Name of exchange the message should be pushed towards |
| `Routing Key` | `q_sqapi` | Name of the queue to push towards. Is required, but will be ignored by RabbitMQ |
| `Host Name` | `mq` | Host of the running RabbitMQ instance |


## Data Store
Local disk is used as storage for the loaded files.


## Metadata Store
Redis is used to store a json structured metadata.


## sqAPI
New data from broker (`Message System`) will trigger aggregation of the newly incoming data,
while all aggregated data will be stored in the storage (`sqAPI Storage`).

If needed, sqAPI also have access to execute queries towards the `Data Store`
and `Metadata Store` for fetching necessary supplements to return to the user.

When a user wants to access the aggregated data, they will connect to the API,
and sqAPI will perform necessary searches in its storage.


## sqAPI Storage
Each sqAPI plugin could have its own database connection,
dependent on its custom data set structure.
In this example its used a Postgres database.
