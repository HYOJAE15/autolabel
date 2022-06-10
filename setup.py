## setup.py
from glob import glob
from os.path import basename, splitext
from setuptools import find_packages, setup

setup(
    name='Auto Labeling Toolkit',
    version='0.1.0',
    packages=find_packages(where='py_script'),
    package_dir={'': 'py_script'},
    py_modules=[splitext(basename(path))[0] for path in glob('py_script/*.py')],
)