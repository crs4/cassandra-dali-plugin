# Adapted to use cassandra-dali-plugin, from
# https://github.com/NVIDIA/DALI/blob/main/docs/examples/use_cases/pytorch/resnet50/main.py
# (Apache License, Version 2.0)

# Cassandra Reader
from cassandra_reader import get_cassandra_reader

try:
    from nvidia.dali.pipeline import pipeline_def
    import nvidia.dali.types as types
    import nvidia.dali.fn as fn
except ImportError:
    raise ImportError(
        "Please install DALI from https://www.github.com/NVIDIA/DALI to run this example."
    )


##################################
### DALI PIPELINE CRATION CODE ###
##################################


def pipeline_transformations(images, labels, is_training, dali_cpu, crop, size):
    dali_device = "cpu" if dali_cpu else "gpu"
    decoder_device = "cpu" if dali_cpu else "mixed"
    # ask HW NVJPEG to allocate memory ahead for the biggest image in the data set to avoid reallocations in runtime
    preallocate_width_hint = 5980 if decoder_device == "mixed" else 0
    preallocate_height_hint = 6430 if decoder_device == "mixed" else 0
    if is_training:
        images = fn.decoders.image_random_crop(
            images,
            device=decoder_device,
            output_type=types.RGB,
            preallocate_width_hint=preallocate_width_hint,
            preallocate_height_hint=preallocate_height_hint,
            random_aspect_ratio=[0.8, 1.25],
            random_area=[0.1, 1.0],
            num_attempts=100,
        )
        images = fn.resize(
            images,
            device=dali_device,
            resize_x=crop,
            resize_y=crop,
            interp_type=types.INTERP_TRIANGULAR,
        )
        mirror = fn.random.coin_flip(probability=0.5)
    else:
        images = fn.decoders.image(images, device=decoder_device, output_type=types.RGB)
        images = fn.resize(
            images,
            device=dali_device,
            size=size,
            mode="not_smaller",
            interp_type=types.INTERP_TRIANGULAR,
        )
        mirror = False

    images = fn.crop_mirror_normalize(
        images.gpu(),
        dtype=types.FLOAT,
        output_layout="CHW",
        crop=(crop, crop),
        mean=[0.485 * 255, 0.456 * 255, 0.406 * 255],
        std=[0.229 * 255, 0.224 * 255, 0.225 * 255],
        mirror=mirror,
    )
    if not dali_device == "gpu":
        labels = labels.gpu()

    return images, labels


@pipeline_def
def create_dali_pipeline_cassandra(
    data_table,
    crop,
    size,
    source_uuids,
    shuffle_every_epoch=True,
    dali_cpu=False,
    is_training=True,
    prefetch_buffers=2,
    shard_id=0,
    num_shards=1,
    io_threads=4,
    comm_threads=1,
    copy_threads=4,
    wait_threads=2,
):

    cass_reader = get_cassandra_reader(
        data_table=data_table,
        prefetch_buffers=prefetch_buffers,
        shard_id=shard_id,
        num_shards=num_shards,
        source_uuids=source_uuids,
        io_threads=io_threads,
        comm_threads=comm_threads,
        copy_threads=copy_threads,
        wait_threads=wait_threads,
        shuffle_every_epoch=shuffle_every_epoch,
        ooo=False,
        slow_start=4,
    )

    images, labels = cass_reader

    images, labels = pipeline_transformations(
        images, labels, is_training, dali_cpu, crop, size
    )

    return (images, labels)


@pipeline_def
def create_dali_pipeline_from_file(
    data_dir,
    crop,
    size,
    dali_cpu=False,
    is_training=True,
    shard_id=0,
    num_shards=1,
):

    images, labels = fn.readers.file(
        file_root=data_dir,
        shard_id=shard_id,
        num_shards=num_shards,
        random_shuffle=is_training,
        pad_last_batch=True,
        name="Reader",
    )

    images, labels = pipeline_transformations(
        images, labels, is_training, dali_cpu, crop, size
    )

    return (images, labels)
