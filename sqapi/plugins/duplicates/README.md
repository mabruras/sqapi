# Duplicates

## Intention
This plugin uses a sha256 hash to map against objects uuid_ref.


## Accepts
All types


## Storage
### Disk
N/A

### Data Structure
Read the [init.sql](./scripts/init.sql) to see the stored data structure.

## Usage
### Endpoints
* `/duplicates/sha/<sha_256>`: Returns all uuid references with the same sha256
* `/duplicates/uuid/<uuid_ref>`: Returns the sha_256 of a specific uuid reference
