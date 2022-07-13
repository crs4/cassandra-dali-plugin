# Copyright 2021-2 CRS4
#
# Use of this source code is governed by an MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.

from tqdm import trange, tqdm
import numpy as np
from time import sleep
import os
import torch
from torchvision import transforms

from nvidia.dali.pipeline import pipeline_def
import nvidia.dali.types as types
import nvidia.dali.fn as fn
from nvidia.dali.plugin.pytorch import DALIGenericIterator

suff="jpg"
src_dir = os.path.join("/data/imagenette-cropped/", suff)

@pipeline_def(batch_size=128, num_threads=10, device_id=1,
              #prefetch_queue_depth=4,
)
def get_dali_pipeline(src_dir):
    images, labels = fn.readers.file(file_root=src_dir, name="Reader")
    images = fn.decoders.image(images, device="mixed", output_type=types.RGB)
    # images = images.gpu()
    labels = labels.gpu()
    return images, labels

pl = get_dali_pipeline(src_dir)
    
# using PyTorch iterator
ddl = DALIGenericIterator(
   [pl], ['data', 'label'],
   reader_name='Reader'
)

for _ in trange(10):
    for data in ddl:
        x, y = data[0]['data'], data[0]['label']
    ddl.reset() # rewind data loader