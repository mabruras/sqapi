# Configuration
This section covers the general configuration for the sqAPI instance,
as well as plugin specific fields and topics.

## Configuration files
sqAPI consist of two types of configuration:
* `sqAPI config`: instance specific
* `plugin config`: plugin specific

The sqAPI config file, is default located in
[sqAPI > conf > sqapi.yml](https://github.com/mabruras/sqapi/blob/master/src/sqapi/resources/sqapi.yml),
but can be overwritten with the `CFG_FILE` environment variable.

The plugin configuration is located in the root directory
of each plugin, named `config.yml` (_not editable_).

When accessing the `config` object from a plugin,
it will be accessible as a single set of configuration.
This means that the configuration defined in sqAPI-config
will be overwritten by the plugin-config.

### Environment Variables
It is supported to use environment variable substitution in the configuration files.
Each of the configuration files can have custom values for a specific environment.
This could be useful when deploying to multiple environments, which then
could use different external systems based on the environment type; `dev`, `test` etc.

##### Example
```yaml
broker:
  type: ${MSG_BROKER_TYPE}
  host: ${MSG_BROKER_HOST}
  port: ${MSG_BROKER_PORT}
```


## Topics
The config object will be populated as a set of topics,
where each topic is a dictionary consistent of the defined fields with values.

The configuration will expose the following topics:
```yaml
packages:
plugin:
broker:
message:
meta_store:
data_store:
database:
active_plugins:
api:
custom:
```

The `plugin` topic is defined for each plugin, and is not intended used outside the defined plugin.

#### sqAPI vs. plugin
What should be defined in which config?
Usually all configuration which is equal across multiple plugins,
should be defined in sqAPI config, like `broker`, `meta_store`, `data_store` and `active_plugins`.

Typical plugin config are topics like `database` and `api`,
since these usually are custom for each sqAPI plugin.

Putting fields in the `custom` topic could be done wherever,
dependent on where the fields are intended to be used.

It is important to note that you are able to overwrite configuration in each plugin.
So if you need to append information to a topic, you do so by defining it in the plugin config.

##### Duplicate Topic
The `database`-topic is quite unique, since sqAPI needs
a place to store the status of each received message.

sqAPI needs a database configuration to store messages,
this does not need to be any of the databases used by the plugins.


### Packages
It is possible to specify python modules for installment or downloading, for each custom sqAPI Plugin.
In the main configuration, it should be defined if custom packages are to be installed or not - default is `False`.

The `install` field is possible to overwrite in the plugin config files,
to avoid the packages of a plugin to be installed or downloaded.
This means that you can deactivate download/installment of dependencies to specific plugins. 

There are different modules that could be run, like `PIP` or `Spacy`,
dependent on the plugins area of responsibility.

##### Example
```yaml
packages:
  install: True # Default is False, if not defined
```

##### Plugin Specific
In each plugin, the module packages should be defined within the module and action it requires.
This ensures documentation in addition to the README of each plugin.
```yaml
packages:
  install: True # Optional in plugin specific config
  pip:
    install:
    - 'spacy'
  spacy:
    download:
    - 'en'
```

The configuration above is translated to: 
```bash
python3 -m pip install spacy
python3 -m spacy install en
```

_(**NOTE:** In the above example the PIP package installment of "Spacy"
must be defined above the Spacey package download of "en", to be executed first)_

This lets sqAPI being able to install and configure each plugin dependencies runtime.
There might be a good idea to pre-install and configure each plugin, to reduce startup time.


### Plugin Details
In addition to the sqAPI config, the core setup will append
information about the plugin within the plugin processor configuration.
This information is possible to overwrite, but is not recommended since it's system generated.

#### Supported Mime
The only part makes sense to overwrite (or even define) in the plugin configurations,
are the `mime_types` covering which mime types the plugin supports.

##### Specific Mime Types
```yaml
plugin:
  mime_types:
  - 'image/jpeg'
  - 'image/png'
  - 'image/gif'
```

##### All Mime Types
```yaml
# Empty list
plugin:
  mime_types:
```
or
```yaml
# Left out field
plugin:
```

##### Example
```yaml
plugin:
  name: 'duplicates'                        # Values set by core processor
  directory: '/opt/app/plugins/duplicates'  # Values set by core processor
```


### Broker
The message broker, usually defined in
[sqAPI configuration](https://github.com/mabruras/sqapi/blob/master/src/sqapi/resources/sqapi.yml),
must contain a reference to the connection details towards the wanted message system.
Usually this would be a broker, but broker-less systems may also be supported.

#### Types
See more details for each Broker type in the
[Connector documentation](https://github.com/mabruras/sqapi/blob/master/resources/docs/CONNECTORS.md)

* RabbitMQ
* Kafka
* ZeroMQ


### Message
The message configuration, usually defined in
[sqAPI configuration](https://github.com/mabruras/sqapi/blob/master/src/sqapi/resources/sqapi.yml),
must contain a details about how the message is formatted and could be parsed.

#### Parser
It must be defined a `parser`, being either `json` or `string`.

##### JSON Parser
Json parser does not need any other configuration,
since it only requires a valid serialized json.

Its fields should be represented within the `fields`,
at least the ones being required.
```yaml
message:
  parser:
    type: 'json'
```

##### String Parser
When using a String parser the string `format` and a `delimiter` should be defined.
This will help sqAPI split each message into the defined format with the field keys.

A format with `uuid|hash` should have the delimiter `|`.
```yaml
message:
  parser:
    type: 'string'
    format: 'uuid|hash'
    delimiter: '|'
```

#### Mime
If the mime type is detected upfront of sqAPI, and is contained within the metadata,
it could be referred to through path within the metadata.

Make sure to use a separator to match the path to look for the mime type.
The following example metadata could be referred through the trailing configuration example.
```json
{
  "root": {
    "wrapper": {
      "mime.type": "application/json"
    }
  }
}
```

```yaml
  mime:
    path: 'root:wrapper:mime.type'
    path_separator: ':'
```

#### Message Fields
Remember to list up minimum required fields of the message (`fields`)
as these will be validated upon received message.

The `data_location`-field is required upon default, and will be enforced as required.
Without these fields, sqAPI will not be able to query for the data content.

The `key`-field, of each field in `fields`, is the representation of the field-name within the message.
This means that a message defining `type` by `mime.type`, should change `key: 'data_type'` to `key: 'mime.type'`.
```yaml
message:
  fields:
    data_location:
      key: 'hash'
      required: True
    meta_location:
      key: 'uuid'
      required: True
```

#### Example
```yaml
message:
  parser:
    type: 'string'
    format: 'uuid|file_path|redis_key|data_type|metadata'
    delimiter: '|'

  mime:
    path: 'mime.type'
    path_separator: '_'

  fields:
    uuid:
      key: 'uuid'
      required: True
    data_location:
      key: 'file_path'
      required: True
    meta_location:
      key: 'redis_key'
      required: False
    type:
      key: 'data_type'
      required: False
    metadata:
      key: 'metadata'
      required: False
```

#### Plugin Specific
This configuration does not really make sense to overwrite in the plugin specific configurations,
since they all is used within the core of sqAPI.


### Metadata Store
The metadata store is also defined by a type and connection details.

It is important to notice that a configuration for Metadata store, is not required.
This is because the metadata is possible to put on the message.
If it is desirable to put the metadata on the message,
the `fields` > `metadata` reference mentioned above could be used.

If the metadata is not detected in the message,
nor any configuration for a metadata storage is defined,
the metadata will be represented as an empty dictionary.

#### Redis
##### Example
```yaml
meta_store:
  type: 'redis'
  host: 'localhost'
  port: 6379
```

##### Plugin Specific
```yaml
# No need to overwrite, but still possible
```


### Data Store
The data store is defined by a type and connection details.

#### Disk
Disk does not have a need for connection details or credentials.

##### Example
```yaml
data_store:
  type: 'disk'
```

##### Plugin Specific
```yaml
# No need to overwrite, but still possible
```


#### Swift
Uses `python3-swiftclient` to connect to a OpenStack Swift instance.

##### Example
```yaml
data_store:
  type: 'swift'
  auth_url: 'http://localhost:8080/auth/v1.0'
  access_key_id: 'test:tester'
  secret_access_key: 'testing'
```

##### Plugin Specific
```yaml
# No need to overwrite, but still possible
```


### Database
The database is usually specific for each sqAPI plugin,
but can be general as well - dependent on your system setup.

Have in mind that there always need to be defined a database connection
in the sqAPI configuration - to be able to handle received messages.

#### Postgres
Uses `psycopg2` to connect towards a PostgreSQL instance.

##### Example
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

##### Plugin Specific
```yaml
# In cases where reuse of the sqAPI-database is intended,
# do not define any in the plugin configuration.
```


### Active Plugins
One of the intentions behind sqAPI is to be able activating only specific plugins,
to keep a separation of concern.
So when using sqAPI, there should explicitly be defined which plugins are intended to run.

If none is listed, all will be activated.
This is in case the sqAPI should run all plugins, to avoid forgetting to list some of them.

**Pro tip**:
The `PLUGIN`-environment variable is intended to create a sqAPI instance with a single plugin running.
This is useful when deploying containers on specific nodes on an orchestrator like Docker Swarm.

_Eg. some logic runs better on a GPU, it might be better to tag some plugins to specific hardware._

##### Example
```yaml
active_plugins:
- duplicates
- thumbnails
```
This will make sqAPI start a loader and/or blueprints, only for each of the plugins listed.
Not that this is possible to overwrite with `PLUGIN`-environment variable.


### API
There isn't much configuration for the API,
since most of the endpoints will be custom for each plugin,
and the developer has full access to their own implementation.

There is only needed a default directory reference,
for where the blueprints are located.

##### Example
```yaml
# It's possible to define a default blueprints directory,
# but not necessary at all - since a plugin might use another directory name.
```

##### Plugin Specific
```yaml
api:
  blueprints_directory: 'blueprints'
```


### Custom
This topic is a wrapper for all your custom configurations.
To keep the variables separate from potential mix-up with the original configurations,
they are put within this wrapped topic.

There are no restrictions for your custom configuration,
and they are not used by the sqAPI core system.
