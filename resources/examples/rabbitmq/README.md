# RabbitMQ
Example setup explaining how sqAPI can be used with RabbitMQ

## Components

| Component | Technology | Description |
| --------- | ---------- | ----------- |
| `Data Store` | `File System` | Data located on disk |
| `Message System` | `RabbitMQ` | Publishes messages to each active `sqAPI`-instance |
| `sqAPI` | `Python` | System for executing queries based on a subscription, fetch, aggregate and expose data |
| `sqAPI Storage` | `PostgreSQL` | Local storage for each `sqAPI`, keeps record of all messages and aggregated data |


## Data Store
Local disk is used as storage for the loaded files.


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
