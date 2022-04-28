# Copyright 2021-2 CRS4
#
# Use of this source code is governed by an MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.

from setuptools import setup
from distutils.core import Extension
from torch.utils import cpp_extension
import pybind11
from glob import glob

import os

print(os.environ["LD_LIBRARY_PATH"])

EXTRA_COMPILE_ARGS = ["-fvisibility=hidden", "-g0"]

cpp_handler = cpp_extension.CppExtension(
    "BPH",
    sorted(glob("cassandradl/cpp/*.cpp")),
    include_dirs=[
        "/usr/include/opencv4",
    ],
    language="c++",
    library_dirs=["/usr/local/lib/x86_64-linux-gnu"],
    libraries=["cassandra", "opencv_core", "opencv_imgcodecs", "python3.8"], 
    extra_compile_args=EXTRA_COMPILE_ARGS,
)

ext_mods = [cpp_handler]

setup(
    name="cassandradl",
    version="0.1",
    author="Francesco Versaci, Giovanni Busonera",
    author_email="francesco.versaci@gmail.com, giovanni.busonera@crs4.it",
    description="Cassandra data loader for ML pipelines",
    packages=["cassandradl"],
    url="https://github.com/bla",
    ext_modules=ext_mods,
    cmdclass={"build_ext": cpp_extension.BuildExtension},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering",
        "Intended Audience :: Science/Research",
    ],
    install_requires=[
        'cassandra-driver',
        'pybind11',
        'opencv-python',
        'tqdm',
    ],
    python_requires=">=3.6",
)
