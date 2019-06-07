# Image Plugin

## Intention
This image plugin is intended to keep information about the images
received by the system.

By extracting EXIF data and serve thumbnails of incoming images.

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
TODO
