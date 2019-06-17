# Sizes

## Intention
This plugin stores the count of metadata fields, and the size of the data payload.


## Accepts
All types


## Storage
### Data Structure
Read the [init.sql](./scripts/init.sql) to see the stored data structure.


## Usage
### Endpoints
`/sizes/lt/<size>`: Returns all object less than the given size
`/sizes/gt/<size>`: Returns all object greater than the given size
