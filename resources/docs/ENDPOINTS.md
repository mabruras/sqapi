## Endpoints
*sqAPI* has some default endpoints activated,
in addition to the active plugins that is running.

These endpoints will be accessible even if there are no active plugins.

### Health Check
_TODO: Not implemented yet_

### Plugins
A complete list of the active plugins are available at URI `/plugins`,
where each plugin contains the following.

#### Output
##### Field Description
* `name`: Name of the plugin
* `blueprints`: List of blueprint in the plugin
  * `package`: Package where the blueprint is located
  * `url_prefix`: Parent endpoint
  * `endpoints`: Rules for this specific blueprint
    * See [rules](#rules) for more details

###### Example
```json
[
  {
    "name": "thumbnails",
    "blueprints": [
      {
        "package": "sqapi.plugins.thumbnails.blueprints.thumbnails",
        "url_prefix": "/thumbnails",
        "endpoints": [
          {
            "function": "sqapi.plugins.thumbnails.blueprints.thumbnails.thumbnail_by_uuid",
            "endpoint": "/thumbnails/%3Cuuid_ref%3E",
            "arguments": [
              "uuid_ref"
            ],
            "methods": [
              "OPTIONS",
              "GET",
              "HEAD"
            ]
          }
        ]
      }
    ]
  }
]
```

### Rules
List all active and available endpoints for the running instance,
available at URI `/rules`.

#### Output
##### Field Description
* `function`: Function name prefixed with package
* `endpoint`: Endpoint for specific function
* `arguments`: List of arguments to the mentioned function
* `Methods`: Supported HTTP methods for the specific endpoint

###### Example
```json
[
  {
    "function": "sqapi.plugins.thumbnails.blueprints.thumbnails.thumbnail_by_uuid",
    "endpoint": "/thumbnails/%3Cuuid_ref%3E",
    "arguments": [
      "uuid_ref"
    ],
    "methods": [
      "OPTIONS",
      "GET",
      "HEAD"
    ]
  }
]
```
