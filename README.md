# Cassandra plugin for NVIDIA DALI

## Overview

This is a plugin that enables data loading from an [Apache Cassandra
DB](https://cassandra.apache.org) into [NVIDIA Data Loading Library
(DALI)](https://github.com/NVIDIA/DALI) (which can be used to load and
preprocess images for Pytorch or TensorFlow).

## Installation

The easiest way to test the cassandra-dali-plugin is by using the
provided Dockerfile, which also contains PyTorch, NVIDIA DALI,
Cassandra C++ and Python drivers, an Apache Cassandra server and
Apache Spark.

The details of how to install the Cassandra Data Loader in a system
which already provides some of the package above can be deduced from
the [Dockerfile](Dockerfile).

For better performance and for data persistence, it is advised to
mount a host directory for Cassandra on a fast disk (e.g.,
`/mnt/fast_disk/cassandra`), as shown in the commands below.

```bash
## Build and run cassandradl docker container
$ docker build -t cassandradl .
$ docker run --rm -it -v /mnt/fast_disk/cassandra:/cassandra/data:rw --cap-add=sys_nice cassandra-dali-plugin

## Inside the Docker container:

## - Start Cassandra server
$ /cassandra/bin/cassandra   # Note that the shell prompt is immediately returned
                             # Wait until "state jump to NORMAL" is shown (about 1 minute)
```

## Dataset examples

- [Imagenette](examples/imagenette/)

## Requirements

cassandra-dali-plugin requires:
- Cassandra C/C++ driver
- Cassandra Python driver
- NVIDIA DALI

All the required packages are already installed in the provided
Dockerfile.

## Authors

Cassandra Data Loader is developed by
  * Francesco Versaci, CRS4 <francesco.versaci@gmail.com>
  * Giovanni Busonera, CRS4 <giovanni.busonera@crs4.it>

## License

cassandra-dali-plugin is licensed under the MIT License.  See LICENSE
for further details.

## Acknowledgment

- Jakob Progsch for his [ThreadPool code](https://github.com/progschj/ThreadPool)
