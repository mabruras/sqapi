# ZeroMQ
This is a document describing how an example system can be created,
with only a message as trigger for the sqAPI execution,
before exposing the data to the end user.

**Note: This is a guide to setup your own example system!**

## Components
This example consist of a minimal set of components,
all intended to populate a central storage unit,
execute specific logic on receive message and expose the aggregated data to the users.

The components are represented by specific technologies in this example,
but it is possible to switch to other similar alternatives.

| Component | Technology | Description |
| --------- | ---------- | ----------- |
| `Data Store` | `File System` | Data located on disk |
| `Message System` | `ZeroMQ` | Publishes messages to each active `sqAPI`-instance |
| `sqAPI` | `Python` | System for executing queries based on a subscription, fetch, aggregate and expose data |
| `sqAPI Storage` | `PostgreSQL` | Local storage for each `sqAPI`, keeps record of all messages and aggregated data |


## Data Store
Local disk is used as storage for the loaded files.


## sqAPI
_Subscription, Query, API_ is a plugin-based component intended to:
* Subscribe to the `Message Broker`
* Query data from `Data Store`
* Query metadata from `Metadata Store`
* Aggregate and store custom data set in `sqAPI Storage`
* Serve aggregated data and metadata through the API

New data from the queue will trigger a query and aggregation of the newly incoming data.
All aggregated data will be stored in a sqAPI specific storage solution (`sqAPI Storage`).
Which database used is dependent on the intentions of the current sqAPI and the custom data set.

When a user wants to access the aggregated data, they will connect to the API,
and the sqAPI will perform necessary searches in its local database.
If needed, sqAPI also have access to execute queries towards the `Data Store`
and `Metadata Store` for fetching necessary supplements to return to the user.


## sqAPI Storage
The sqAPI storage is a chosen storage solution, based on the configuration.
Each sqAPI plugin could have its own database connection, dependent on its custom data set structure.

### Preparation
Independent of storage type, there should be a setup function made available,
to create necessary structures to fill the following needs:
* Failed messages
  * Messages failed processing should be stored locally
  * Messages failed in query step, should be retried after a defined amount of time
* Modified data
  * Aggregated data should be stored locally for searches and sqAPI logic
