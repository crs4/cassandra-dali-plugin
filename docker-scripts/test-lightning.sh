#! /bin/bash -x
set -e

cd examples/lightning
ssh root@cassandra 'SSL_VALIDATE=false /opt/cassandra/bin/cqlsh --ssl -e "DROP KEYSPACE IF EXISTS imagenette;"'
cat create_tables.cql | ssh root@cassandra 'SSL_VALIDATE=false /opt/cassandra/bin/cqlsh --ssl'
python3 extract_serial.py /tmp/imagenette2-320 --split-subdir=train --data-table imagenette.data_train --metadata-table imagenette.metadata_train
python3 extract_serial.py /tmp/imagenette2-320 --split-subdir=val --data-table imagenette.data_val --metadata-table imagenette.metadata_val
rm -f {train,val}.rows
python3 cache_uuids.py --metadata-table=imagenette.metadata_train --rows-fn=train.rows
python3 cache_uuids.py --metadata-table=imagenette.metadata_val --rows-fn=val.rows
python3 train_model.py --num-gpu 1 -a resnet50 --b 64 --workers 4 --lr=1.0e-3 --epochs 1 \
                       --train-data-table imagenette.data_train --train-rows-fn train.rows \
                       --val-data-table imagenette.data_val --val-rows-fn val.rows
echo "--- OK ---"
