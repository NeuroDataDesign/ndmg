

# ndmg

![Downloads shield](https://img.shields.io/pypi/dm/ndmg.svg)
[![](https://img.shields.io/pypi/v/ndmg.svg)](https://pypi.python.org/pypi/ndmg)
![](https://travis-ci.org/neurodata/ndmg.svg?branch=master)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.1161284.svg)](https://doi.org/10.5281/zenodo.1161284)
[![Code Climate](https://codeclimate.com/github/neurodata/ndmg/badges/gpa.svg)](https://codeclimate.com/github/neurodata/ndmg)
[![DockerHub](https://img.shields.io/docker/pulls/bids/ndmg.svg)](https://hub.docker.com/r/bids/ndmg)
[![OpenNeuro](http://bids.neuroimaging.io/openneuro_badge.svg)](https://openneuro.org)

![](./docs/nutmeg.png)

NeuroData's MR Graphs package, **ndmg** (pronounced "***nutmeg***"), is a turn-key pipeline which combines structural, diffusion, and functional\* MRI data to estimate multi-resolution connectomes reliably and scalably.

## Contents

- [Overview](#overview)
- [System Requirements](#system-requirements)
- [Installation Guide](#installation-guide)
- [Docker](#docker)
- [Tutorial](#tutorial)
- [Outputs](#outputs)
- [Usage](#usage)
- [Example Datasets](#example-datasets)
- [Documentation](#documentation)
- [License](#license)
- [Manuscript Reproduction](#manuscript-reproduction)
- [Issues](#issues)

## Overview

The **ndmg** pipeline has been developed as a one-click solution for human connectome estimation by providing robust and reliable estimates of connectivity across a wide range of datasets. The pipelines are explained and derivatives analyzed in our pre-print, available on [BiorXiv](https://www.biorxiv.org/content/early/2017/09/16/188706).

## System Requirements

The **ndmg** pipeline:
 - was developed and tested primarily on Mac OSX, Ubuntu (12, 14, 16, 18), and CentOS (5, 6);
 - made to work on Python 3.6;
 - is wrapped in a [Docker container](https://hub.docker.com/r/bids/ndmg/);
 - has install instructions via a [Dockerfile](https://github.com/BIDS-Apps/ndmg/blob/master/Dockerfile#L6);
 - requires no non-standard hardware to run;
 - has key features built upon FSL, Dipy, Nibabel, Nilearn, Networkx, Numpy, Scipy, Scikit-Learn, and others;
 - takes approximately 1-core, 8-GB of RAM, and 1 hour to run for most datasets.

While **ndmg** is quite robust to Python package versions (with only few exceptions, mentioned in the [installation guide](#installation-guide)), an *example* of possible versions (taken from the **ndmg** Docker Image with version `v0.2.0`) is shown below. Note: this list excludes many libraries which are standard with a Python distribution, and a complete list with all packages and versions can be produced by running `pip freeze` within the Docker container mentioned above.

```
awscli==1.16.210 , boto3==1.9.200 , botocore==1.12.200 , colorama==0.3.9 , configparser>=3.7.4 , Cython==0.29.13 , dipy==0.16.0 ,
duecredit==0.7.0 , fury==0.3.0 , graspy==0.0.3 , ipython==7.7.0 , matplotlib==3.1.1 , networkx==1.9 , nibabel==2.5.0 , 
nilearn==0.5.2 , numpy==1.17.0 , pandas==0.25.0, Pillow==6.1.0 , plotly==1.12.9, pybids==0.6.4 , python-dateutil==2.8.0 , 
PyVTK==0.5.18 , requests==2.22.0 , s3transfer==0.2.1 , setuptools>=40.0 scikit-image==0.13.0 , scikit-learn==0.21.3 , 
scipy==1.3.0 , sklearn==8.0 , vtk==8.1.2
```

## Installation Guide

**ndmg** relies on [FSL](http://fsl.fmrib.ox.ac.uk/fsl/fslwiki/FslInstallation), [Dipy](http://nipy.org/dipy/), [networkx](https://networkx.github.io/), and [nibabel](http://nipy.org/nibabel/), [numpy](http://www.numpy.org/) [scipy](http://www.scipy.org/), [scikit-learn](http://scikit-learn.org/stable/), [scikit-image](http://scikit-image.org/), [nilearn](http://nilearn.github.io/). You should install FSL through the instructions on their website, then follow install other Python dependencies with the following:

    pip install ndmg
 
The only known packages which require a specific version are `plotly` and `networkx`, due to backwards-compatability breaking changes.

Finally, you can install **ndmg** either from `pip` or Github as shown below. Installation shouldn't take more than a few minutes, but depends on your internet connection.

### Install from pip

    pip install ndmg

### Install from Github

    git clone https://github.com/neurodata/ndmg.git
    cd ndmg
    python install .

## Docker

**ndmg** is available through Dockerhub, and can be run directly with the following container (and any additional options you may require for Docker, such as volume mounting):

    docker run -ti --entrypoint /bin/bash bids/ndmg

**ndmg** containers can also be made from Github. Download the most recent version of ndmg from github and in the ndmg directory created, there should be a file called Dockerfile. Create a Docker image using the command:

    docker build --rm -f "path/to/docker/file" -t ndmg:whateverlabelyouwant ndmg

Additional information about building Docker images can be found [here](https://docs.docker.com/engine/reference/commandline/image_build/).
Creating the Docker image should take several minutes if this is the first time you have used this docker file.
Create a Docker contianer from the image using the following command
In order to create a docker container from the docker image and enter it, use the following command:

    docker run -it --entrypoint /bin/bash ndmg:whateverlabelyouwant
   

## Tutorial


## Outputs
The outputs generated by the **ndmg** pipeline are organized as:
```
output
     anat
          preproc
               Files created during the preprocessing stage of the pipeline
                   -
          registered
               a
     dwi
          fiber
          preproc
          roi-connectomes
          tensor
     qa
          adjacency
          fibers
          graphs
          graphs_plotting
          mri
          reg
          tensor
     tmp
          reg_a
          reg_m
```

## Usage

The **ndmg** pipeline can be used to generate connectomes as a command-line utility on [BIDS datasets](http://bids.neuroimaging.io) with the following:

    ndmg_bids /input/bids/dataset /output/directory

Note that more options are available which can be helpful if running on the Amazon cloud, which can be found and documented by running `ndmg_bids -h`. If you do not have a BIDS organized dataset, you an use a slightly more complicated interface which is made available and is documented with `ndmg_pipeline -h`.

If running with the Docker container shown above, the `entrypoint` is already set to `ndmg_bids`, so the pipeline can be run directly from the host-system command line as follows:

    docker run -ti -v /path/to/local/data:/data bids/ndmg /data/ /data/outputs

## Example Datasets

Derivatives have been produced on a variety of datasets, all of which are made available on [our website](http://m2g.io). Each of these datsets is available for access and download from their respective sources. Alternatively, example datasets on the [BIDS website](http://bids.neuroimaging.io) which contain diffusion data can be used and have been tested; `ds114`, for example.

## Documentation

Check out some [resources](http://m2g.io) on our website, or our [function reference](https://ndmg.neurodata.io/) for more information about **ndmg**.

## License

This project is covered under the [Apache 2.0 License](https://github.com/neurodata/ndmg/blob/ndmg/LICENSE.txt).

## Manuscript Reproduction

The figures produced in our manuscript linked in the [Overview](#overview) are all generated from code contained within Jupyter notebooks and made available at our [paper's Github repository](https://github.com/neurodata/ndmg-paper).

## Issues

If you're having trouble, notice a bug, or want to contribute (such as a fix to the bug you may have just found) feel free to open a git issue or pull request. Enjoy!
