# Template Plugin
This template plugin is based on the [Sizes plugin](../../../sqapi/plugins/sizes/README.md)
extended with more code comments and explanation for the developers.

## Intention
This header should contain a short description of why this plugin exists.

Eg.:
_This plugin stores the count of metadata fields, and the size of the data payload._


## Accepts
Here it should be listed all accepted types that this plugin handles.

Example for plugin supporting image types:
```
- image/jpeg
- image/gif
- image/png
```

For plugins that accepts everything:
```
All types
```


## Storage
Everything about storage that the user should be aware of.
Like specific structure of storage,
and what type of storage this plugin is using - of if there is some it does not support.

### Data Structure
Read the [init.sql](./scripts/init.sql) to see the stored data structure.


## Usage
Good practice to mention how this plugin is supposed to be used by the end user.
Are there any specific details for the endpoints that the user needs to know,
or even which endpoints do exist.

### Endpoints
* `/sizes/lt/<size>`: Returns all object less than the given size
* `/sizes/gt/<size>`: Returns all object greater than the given size
