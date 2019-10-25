#!/usr/bin/env python

from setuptools import setup, Extension
from ndmg import __version__


setup(
    name="ndmg",
    packages=["ndmg", "ndmg.stats", "ndmg.utils", "ndmg.scripts"],
    include_package_data=True,
    version=__version__,
    entry_points={
        "console_scripts": [
            "ndmg_bids=ndmg.scripts.ndmg_bids:main",  # for backwards compatibility
            "ndmg=ndmg.scripts.ndmg_bids:main",
            "ndmg_dwi_pipeline=ndmg.scripts.ndmg_dwi_pipeline:main",
            "ndmg_cloud=ndmg.scripts.ndmg_cloud:main",
        ]
    },
    description="Neuro Data MRI to Graphs Pipeline",
    author="Derek Pisner, Alex Loftus, Greg Kiar, Eric Bridgeford, and Will Gray Roncal",
    author_email="dpisner@utexas.edu, aloftus2@jhu.edu, gkiar@jhu.edu, wgr@jhu.edu, ebridge2@jhu.edu",
    url="https://github.com/neurodata/ndmg",
    download_url="https://github.com/neurodata/ndmg/tarball/" + __version__,
    keywords=["connectome", "mri", "pipeline"],
    classifiers=["Programming Language :: Python :: 3.6"],
    install_requires=[
        "numpy",
        "nibabel",
        "dipy",
        "scipy",
        "python-dateutil",
        "pandas",
        "boto3",
        "awscli",
        "matplotlib",
        "nilearn",
        "sklearn",
        "vtk",
        "pyvtk",
        "fury",
        "requests",
        "plotly",
        "pybids",
        "setuptools>=40.0",
        "scikit-image",
        "networkx",
        "configparser>=3.7.4",
        "pytest",
    ],
)
