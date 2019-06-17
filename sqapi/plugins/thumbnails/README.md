# Thumbnails

## Intention
This plugin is intended to create, store and serve thumbnails, for each incoming image file.


## Accepts
Image types; `image/jpeg`, `image/png`, `image/gif`


## Storage
### Disk
The thumbnails are stored directly at the disk, within a configured directory.
```yaml
custom:
  thumb_dir: 'files/thumbnails'
```

### Data Structure
Read the [init.sql](./scripts/init.sql) to see the stored data structure.

## Usage
### Endpoints
* `/thumbnails/<uuid_ref>`: returns a thumbnail base on uuid_ref, it it exists
