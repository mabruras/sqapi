# sqAPI Loader / API
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
| `Data Loader` | `Script` | Loading data into `Data Store`, `Metadata Store` and `Message Broker` |
| `Data Store` | `Xubuntu file system` | Keeping original incoming files |
| `Metadata Store` | `N/A` | Metadata is included in message |
| `Message System` | `ZeroMQ` | Publishes messages to each active `sqAPI`-instance |
| `sqAPI` | `Python` | System for executing queries based on a subscription, fetch, aggregate and expose data |
| `sqAPI Storage` | `PostgreSQL` | Local storage for each `sqAPI`, keeps record of all messages and aggregated data |

