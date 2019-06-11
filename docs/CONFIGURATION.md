# Configuration
This section covers the general configuration for the sqAPI instance,
as well as plugin specific fields and topics.

## Configuration files
sqAPI consist of two types of configuration:
* `sqAPI config`: instance specific
* `plugin config`: plugin specific

The sqAPI config file, is default located in [sqAPI > conf > sqapi.yml](sqapi/conf/sqapi.yml),
but can be overwritten with the `CFG_FILE` environment variable.

The plugin config is located in the plugin root directory, named `config.yml` (_not editable_).

When accessing the `config` object from a plugin,
it will be accessible as a single set of configuration.


## Topics
The config object will be populated as a set of topics,
where each topic is a dictionary consistent of the defined fields with values.

Typically the configuration exposes the following topics:
```yaml
plugin:
msg_broker:
meta_store:
data_store:
database:
active_plugins:
api:
custom:
```

The `plugin` topic is defined for each plugin,
and is not intended used outside the defined plugin.

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
The message broker, usually defined in [sqAPI configuration](../conf/sqapi.yml),
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
To accept all mime-types sent, do *not* define any fields.
```yaml
msg_broker:
  supported_mime:
  - 'image/jpeg'
  - 'image/png'
  - 'image/gif'
```


### Metadata Store
The metadata store is also defined by a type and connection details.

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
Currently there is only support for `disk`, and do not require connection details.

##### Example
```yaml
data_store:
  type: 'disk'
```

##### Plugin Specific
```yaml
# No need to overwrite, but still possible
```


### Database
The database is usually specific for each sqAPI plugin,
but can be general as well - dependent on your system setup.

##### Example
```yaml
# It isn't recommended to define this at sqAPI top-level configuration
```

##### Plugin Specific
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


### Active Plugins
One of the intentions behind sqAPI is to be able activating only specific plugins,
to keep a separation of concern.
So when using sqAPI, there should explicitly be defined which plugins are intended to run.

If none is listed, all will be activated.
This is in case the sqAPI should run all plugins, to avoid forgetting to list some of them.

##### Example
```yaml
active_plugins:
- duplicates
- thumbnails
```
This will make sqAPI start a loader and/or blueprints, only for each of the plugins listed.

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
