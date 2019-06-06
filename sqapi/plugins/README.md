# Plugins

## About
Collection directory for custom business logic.
All different sqAPI logic elements are to be imported as plugins.
This README defines how to develop new plugins,
what is required and recommended when developing plugins for sqAPI.


## Requirements
There are some technical requirements for a plugin to be able to load into sqAPI

### Structure
The folder structure of a plugin is as follows:
```bash
sqapi/plugins/                 # Parent Plugins collection directory
└── plugin_name                # Plugin directory
    ├── blueprints             # Directory for keeping blueprints
    │   ├── endpoints.py       # Blueprints for specific endpoints
    │   └── __init__.py        # 
    ├── config.yml             # Plugin specific configuration - overwrites sqAPI configuration
    ├── __init__.py            # Execution definition : See more below "Business logic"
    ├── scripts                # Normal directory for keeping SQL scripts
    │   └── insert_item.sql    # Specific SQL script to use in
    └── README.md              # Description of the plugin
```

#### Blueprints
Within the blueprints directory,
there should be created a file for each area of concern.
If you want to keep logic for multiple data,
you'll split them into two separate blueprints. 

Eg.:
* `./blueprints/images.py` - (Serves `/images/*`)
* `./blueprints/thumbnails.py` - (Serves `/thumbnails/*`)

Each of the blueprints will be automatically picked up, and referenced to by `bp`.
sqAPI will not register the blueprint if the variable name is incorrect.

Remember `__init__.py`, to make the blueprints available for import to sqAPI.


#### Configuration
The configuration file: `config.yml`, it's name is not changeable.

The plugin-specific configuration is used to override default
configuration from [sqAPI-config](../conf/sqapi.yml).

The configuration can be extended to what ever
you want to use within the business logic.
If a field already exists in the default configuration,
it will be overwritten for each of the plugins overriding it.

Typical usage, will be for defining database connection,
as well as supported mime types.


#### Business Logic
All business logic is defined within the `__init__.py`, for the specific plugin.
When a plugin is triggered, sqAPI looks for a definition of `execute`.
If the `execute` function is not available, it will not import the module.

Minimum setup:
```python
def execute(config, database, message: dict, metadata: dict, data: bytes):
    pass
```

##### Arguments
###### Config
This is the complete configuration for this plugin,
as mentioned within the [Configuration](#configuration).

###### Database
The database object is selected based up on what is defined in the plugins specifications.

Each type of database should always be available for the following methods:
```python
def execute_script(self, script_path: str, **kwargs): pass
def execute_query(self, query: str, **kwargs): pass
```

The script_path is intended to execute your custom plugin scripts.
The kwargs are intended to be replaceable variables within the script.

This depends on the database module implementation,
and what kind of system is running as database.

###### Message
This is the received message, from the message broker,
represented as a dictionary.

###### Metadata
Metadata fetched from the `metadata store`, as dictionary.

###### Data
Data object fetched from the `data store`, in bytes.


#### Database Scripts

#### README.md
Information about this specific plugin.
This will be exposed through one of the default sqAPI endpoints,
so please make the README understandable and nicely formatted.


### Configuration
TODO


## Tips/Tricks
TODO


## Available variables
TODO
