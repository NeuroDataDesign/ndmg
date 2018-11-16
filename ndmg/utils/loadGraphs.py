#!/usr/bin/env python

# Copyright 2014 Open Connectome Project (http://openconnecto.me)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

# loadGraphs.py
# Created by Greg Kiar on 2016-05-11.
# Email: gkiar@jhu.edu

from __future__ import print_function

from collections import OrderedDict
import numpy as np
import networkx as nx
import os


def loadGraphs(filenames, verb=False):
    """
    Given a list of files, returns a dictionary of graphs
    Required parameters:
        filenames:
            - List of filenames for graphs
    Optional parameters:
        verb:
            - Toggles verbose output statements
    """
    #  Initializes empty dictionary
    if type(filenames) is not list:
        filenames = [filenames]
    gstruct = OrderedDict()
    vlist = set()
    for idx, files in enumerate(filenames):
        if verb:
            print("Loading: " + files)
        #  Adds graphs to dictionary with key being filename
        fname = os.path.basename(files)
        try:
            gstruct[fname] = loadGraph(filename)
            vlist |= set(gstruct[fname].nodes())
        except:
            print("%s is not csv format. Skipping...".format(fname))
    for k, v in gstruct.items():
        vtx_to_add = list(np.setdiff1d(list(vlist), list(v.nodes())))
        [gstruct[k].add_node(vtx) for vtx in vtx_to_add]
    return gstruct

def loadGraph(filename, verb=False):
    graph = nx.read_weighted_edgelist(filename, delimiter=',')
    return graph 
