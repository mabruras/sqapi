# Configuration
This section covers the general configuration for the sqAPI instance,
as well as plugin specific fields and topics.

## Configuration files
sqAPI consist of two types of configuration:
* `sqAPI config`: instance specific
* `plugin config`: plugin specific

The sqAPI config file, is default located in
[sqAPI > conf > sqapi.yml](https://github.com/mabruras/sqapi/blob/master/sqapi/conf/sqapi.yml),
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
msg_broker:
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
msg_broker:
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
should be defined in sqAPI config, like `msg_broker`, `meta_store`, `data_store` and `active_plugins`.

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
It is possible to specify PIP packages to install for each custom sqAPI Plugin.
In the main configuration, it should be defined
if custom packages are to be installed or not - default is `True`.

The `install` field is possible to overwrite in the plugin config files,
to avoid the packages of a plugin to be installed.

##### Example
```yaml
packages:
  install: True # Default is True, if not defined
```

##### Plugin Specific
In each plugin, the PIP packages should be defined.
This ensures documentation in addition to the README of each plugin.
```yaml
packages:
  install: True # Optional in plugin specific config
  pip:
  - 'Pillow'
```


### Plugin Details
In addition to the sqAPI config, the core setup will append
information about the plugin within the plugin processor configuration.
This information is possible to overwrite, but is not recommended since it's system generated.

##### Example
```yaml
plugin:
  name: 'duplicates'                        # Values set by core processor
  directory: '/opt/app/plugins/duplicates'  # Values set by core processor
```


### Message Broker
The message broker, usually defined in
[sqAPI configuration](https://github.com/mabruras/sqapi/blob/master/sqapi/conf/sqapi.yml),
must contain a reference to the type of broker and connection details.

Remember to list up minimum required fields of the message (`message_fields`)
as these will be validated upon received message.

##### Example
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
```

##### Plugin Specific
To overwrite and/or append, add specific mime types to support.
```yaml
msg_broker:
  supported_mime:
  - 'image/jpeg'
  - 'image/png'
  - 'image/gif'
```
To accept all mime-types sent, do *not* define any fields.
```yaml
# Empty list
msg_broker:
  supported_mime:
```
or
```yaml
# Left out field
msg_broker:
```


### Metadata Store
The metadata store is also defined by a type and connection details.

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
