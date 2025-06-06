# Training a model by using a split file
In this example we will train a classifier for the [Imagenette2-320
dataset](https://github.com/fastai/imagenette) (a subset of ImageNet)
as a Cassandra dataset and then read the data into NVIDIA DALI.
The raw files are already present in the `/tmp` directory of the
provided [Docker container](../../README.md#running-the-docker-container),
from which the following commands can be run.

Before starting the training process, we will see how to store data
into the database and the procedure of generating a split file. This
file will contain essential information, including training and
validation splits, which will serve as input for the training
application.

## Store imagenette dataset to Cassandra DB
The following commands will create the data and metadata tables within
the Cassandra DB and store all imagenette images to it:

```bash
# - Create the tables in the Cassandra DB
$ cd examples/splitfile/
$ cat create_tables.cql | ssh root@cassandra /opt/cassandra/bin/cqlsh

# - Fill the tables with data and metadata
$ python3 extract_serial.py /tmp/imagenette2-320 --split-subdir=train --data-table=imagenette.data --metadata-table=imagenette.metadata
$ python3 extract_serial.py /tmp/imagenette2-320 --split-subdir=val --data-table=imagenette.data --metadata-table=imagenette.metadata

## Create a split file
Once the data is in the database, we can create a split file by running the ```create_split.py``` script. To view the different options available for the script, we can use the command:

```bash
python3 create_split.py --help
```

That returns the following options:

```
Usage: create_split.py [OPTIONS]

Create Split: a splitfile generator starting from data stored on a Cassandra db.

Options:
  -d, --data-table=STR          Specify the Cassandra datatable (i.e.: keyspace.tablename)
  -m, --metadata-table=STR      Specify the metadata table (i.e.: keyspace.tablename)
  --metadata-ifn=STR            The input filename of previous cached metadata
  --metadata-ofn=STR            The filename to cache  metadata read from db
  -o, --split-ofn=STR           The name of the output splitfile
  -r, --split-ratio=TOLIST      a comma separated values list that specifies the data proportion among desired splits (default: [8, 2])
  -b, --balance=PARSE_BALANCE   balance configuration among classes for each split (it can be a string ('original', 'random') or a a comma separated values
                                list with one entry for each class (default: original)

Other actions:
  -h, --help                    Show the help
```

To create a training and validation split from the training table
images in Imagenette, we can use the following command:

```bash
python3 create_split.py -d imagenette.data -m imagenette.metadata -r 8,2 -o imagenette_splitfile.pckl
```

The execution of this command will result in the creation of an output
file that contains all the relevant information for training a
model. This includes 80% of the images from the database table, which
will serve as the training data, while the remaining 20% will be used
for model validation. The output file is structured as a Python
dictionary, with the `split` key containing a list of arrays, one for
each split, that store the selected samples. Below is an example of a
splitfile generated by the command, which contains all the necessary
data retrieval information from the database

```python
{'data_table': 'imagenette.data',
 'data_id_col': 'id',
 'data_label_col': 'label',
 'metadata_table': 'imagenette.metadata',
 'medadata_id_col': 'id',
 'metadata_label_col': 'label',
 'data_col': 'data',
 'label_type': 'int',
 'row_keys': array([UUID('62842147-18e4-4447-a2eb-a185427aca73'),
        UUID('fd77ab8a-326d-46a5-a95b-77ce7ef92f33'),
        UUID('9be2a98e-bd6e-4fb0-8595-bbaaa5de4ce0'), ...,
        UUID('80540bb4-d57a-46cc-aa0b-d2490c6e9eb4'),
        UUID('94472c7e-1ead-4499-9bce-6e54249c818a'),
        UUID('0f155548-2033-45b2-ac9b-3d0c43738765')], dtype=object),
 'split': [array([11670,  7805,   171, ...,  7043,  5710,  9004]),
  array([1136, 9020, 8754, ..., 7620,  991, 8463])],
 'num_classes': 10}
```

To prevent the need to retrieve metadata from the database each time a
new split is created, you can save the metadata to a file and specify
its name using the CLI option `--metadata-ofn`. For example, by
executing:

```bash
python3 create_split.py -d imagenette.data -m imagenette.metadata -r 8,2 --metadata-ofn metadata.cache -o imagenette_splitfile.pckl
```

Next time, when generating a new split, you can skip passing the
database information by utilizing the CLI option `--metadata-ifn`,
which takes the filename of the cached metadata file as input:

```bash
python3 create_split.py --metadata-ifn metadata.cache -r 8,2 -o imagenette_splitfile.pckl
```

Caching the metadata table to a file can be time-saving when creating
new splits, especially if the size of the metadata table is large.


## Multi-GPU training using the split file

To train and validate a model using the split file that has been
generated, simply run the following command:

```bash
$ torchrun --nproc_per_node=1 distrib_train_from_cassandra.py --split-fn imagenette_splitfile.pckl \
  -a resnet50 --dali_cpu --b 128 --loss-scale 128.0 --workers 4 --lr=0.4 --opt-level O2
```

The split file specified by the mandatory `--split-fn` option contains
all the necessary information to retrieve the appropriate training and
validation samples from the database.

The training and validation split can be specified using the CLI
options `--train-index` and `--val-index`. The default values for
these options are 0 and 1, respectively, which means that the first
row (row 0) of the array in the split field of the split file is
utilized as the training dataset, while the second row (row 1) is
employed for the validation stage.

So, assuming that the command:

```bash
python3 create_split.py --metadata-ifn metadata.cache -r 2,8 -o imagenette_splitfile.pckl
```

creates a split where the first split contains 20% of the data from
the database table, you would likely want to specify the training and
validation indices as follows:

```bash
$ torchrun --nproc_per_node=1 distrib_train_from_cassandra.py --split-fn imagenette_splitfile.pckl --train-index 1 \
  --val-index 0 -a resnet50 --dali_cpu --b 128 --loss-scale 128.0 --workers 4 --lr=0.4 --opt-level O2
```
