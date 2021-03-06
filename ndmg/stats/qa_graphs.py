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

# qa_graphs.py
# Created by Greg Kiar on 2016-05-11.
# Email: gkiar@jhu.edu
# Edited by Eric Bridgeford.

import warnings

warnings.simplefilter("ignore")
from argparse import ArgumentParser
from collections import OrderedDict
from subprocess import Popen
from scipy.stats import gaussian_kde, rankdata
from ndmg.utils import loadGraphs
from os import path as op
import numpy as np
import nibabel as nb
import networkx as nx
import pickle
import sys
import os


def compute_metrics(fs, outdir, atlas, verb=False, modality="dwi"):
    """
    Given a set of files and a directory to put things, loads graphs and
    performs set of analyses on them, storing derivatives in a pickle format
    in the desired output location.

    Required parameters:
        fs:
            - Dictionary of lists of files in each dataset
        outdir:
            - Path to derivative save location
        atlas:
            - Name of atlas of interest as it appears in the directory titles
    Optional parameters:
        verb:
            - Toggles verbose output statements
    """
    print(atlas)
    gr = loadGraphs(fs, modality=modality, verb=verb)
    if modality == "func":
        graphs = binGraphs(gr)
    else:
        graphs = gr

    nodes = nx.number_of_nodes(list(graphs.values())[0])
    #  Number of non-zero edges (i.e. binary edge count)
    print("Computing: NNZ")
    nnz = OrderedDict((subj, len(nx.edges(graphs[subj]))) for subj in graphs)
    write(outdir, "number_non_zeros", nnz, atlas)
    print(("Sample Mean: %.2f" % np.mean(list(nnz.values()))))

    # Scan Statistic-1
    print("Computing: Max Local Statistic Sequence")
    temp_ss1 = scan_statistic(graphs, 1)
    ss1 = temp_ss1
    write(outdir, "locality_statistic", ss1, atlas)
    show_means(temp_ss1)

    if modality == "func":
        graphs = rankGraphs(gr)
        wt_args = {"weight": "weight"}
    else:
        wt_args = {}

    #   Clustering Coefficients
    print("Computing: Clustering Coefficient Sequence")
    temp_cc = OrderedDict(
        (subj, list(nx.clustering(graphs[subj], **wt_args).values())) for subj in graphs
    )
    ccoefs = temp_cc
    write(outdir, "clustering_coefficients", ccoefs, atlas)
    show_means(temp_cc)

    #  Degree sequence
    print("Computing: Degree Sequence")
    test = OrderedDict()
    total_deg = OrderedDict(
        (subj, np.array(list(dict(nx.degree(graphs[subj], **wt_args)).values())))
        for subj in graphs
    )
    ipso_deg = OrderedDict()
    contra_deg = OrderedDict()
    for subj in graphs:  # TODO GK: remove forloop and use comprehension maybe?
        g = graphs[subj]
        N = len(list(g.nodes()))
        LLnodes = list(g.nodes())[0 : N / 2]  # TODO GK: don't assume hemispheres
        LL = g.subgraph(LLnodes)
        LLdegs = [LL.degree(**wt_args)[n] for n in LLnodes]

        RRnodes = list(g.nodes())[N / 2 : N]  # TODO GK: don't assume hemispheres
        RR = g.subgraph(RRnodes)
        RRdegs = [RR.degree(**wt_args)[n] for n in RRnodes]

        LRnodes = g.nodes()
        ipso_list = LLdegs + RRdegs
        degs = [g.degree(**wt_args)[n] for n in LRnodes]
        contra_deg[subj] = [a_i - b_i for a_i, b_i in zip(degs, ipso_list)]
        ipso_deg[subj] = ipso_list
        # import pdb; pdb.set_trace()

    deg = {"total_deg": total_deg, "ipso_deg": ipso_deg, "contra_deg": contra_deg}
    write(outdir, "degree_distribution", deg, atlas)
    show_means(total_deg)
    #  Edge Weights
    if modality == "dwi":
        print("Computing: Edge Weight Sequence")
        temp_ew = OrderedDict(
            (
                s,
                [
                    graphs[s].get_edge_data(e[0], e[1])["weight"]
                    for e in graphs[s].edges()
                ],
            )
            for s in graphs
        )
        ew = temp_ew
        write(outdir, "edge_weight", ew, atlas)
        show_means(temp_ew)
    else:
        temp_pl = OrderedDict()
        print("Computing: Path Length Sequence")
        nxappl = nx.all_pairs_dijkstra_path_length
        for s in graphs:
            apd = nxappl(graphs[s])
            # iterate over the nodes to find the average distance to each node
            avg_path = [np.nanmean(list(v.values())) for k, v in apd.items()]
            temp_pl[s] = np.array(avg_path)
        pl = temp_pl
        write(outdir, "path_length", pl, atlas)
        show_means(pl)

    # Eigen Values
    print("Computing: Eigen Value Sequence")
    laplac = OrderedDict(
        (subj, nx.normalized_laplacian_matrix(graphs[subj])) for subj in graphs
    )
    eigs = OrderedDict(
        (subj, np.sort(np.linalg.eigvals(laplac[subj].A))[::-1]) for subj in graphs
    )
    write(outdir, "eigen_sequence", eigs, atlas)
    print(
        (
            "Subject Maxes: "
            + ", ".join(["%.2f" % np.max(eigs[key]) for key in list(eigs.keys())])
        )
    )

    # Betweenness Centrality
    print("Computing: Betweenness Centrality Sequence")
    nxbc = nx.algorithms.betweenness_centrality
    temp_bc = OrderedDict(
        (subj, list(nxbc(graphs[subj], **wt_args).values())) for subj in graphs
    )
    centrality = temp_bc
    write(outdir, "betweenness_centrality", centrality, atlas)
    show_means(temp_bc)

    # Mean connectome
    print("Computing: Mean Connectome")
    nxnp = nx.to_numpy_matrix
    adj = OrderedDict(
        (subj, nxnp(graph, nodelist=sorted(graph.nodes())))
        for subj, graph in graphs.items()
    )
    mat = np.zeros(list(adj.values())[0].shape)
    for subj in adj:
        mat += adj[subj]
    mat = mat / len(list(adj.keys()))
    write(outdir, "study_mean_connectome", mat, atlas)


def show_means(data):
    print(
        (
            "Subject Means: "
            + ", ".join(["%.2f" % np.mean(data[key]) for key in list(data.keys())])
        )
    )


def binGraphs(graphs, thr=0.1):
    """
    Binarizes a set of graphs given a threshold.

    Required Parameters:
        graphs:
            - a list of graphs.
        thr:
            - the threshold below which edges will be assumed disconnected.
              .1 is chosen as default according to discriminability results.
    """
    binGraphs = {}
    for subj, graph in graphs.items():
        bin_graph = nx.Graph()
        for (u, v, d) in graph.edges(data=True):
            if d["weight"] > thr:
                bin_graph.add_edge(u, v, weight=1)
        binGraphs[subj] = bin_graph
    return binGraphs


def rankGraphs(graphs):
    """
    Ranks the edges in each element of a list of graphs.

    Required Parameters:
        graphs:
            - a list of graphs.
    """
    rankGraphs = {}
    for subj, graph in graphs.items():
        rgraph = nx.Graph()
        edge_ar = np.asarray([x[2]["weight"] for x in graph.edges(data=True)])
        rank_edge = rankdata(edge_ar)  # rank the edges
        for ((u, v, d), rank) in zip(graph.edges(data=True), rank_edge):
            rgraph.add_edge(u, v, weight=rank)
        rankGraphs[subj] = rgraph
    return rankGraphs


def scan_statistic(mygs, i):
    """
    Computes scan statistic-i on a set of graphs

    Required Parameters:
        mygs:
            - Dictionary of graphs
        i:
            - which scan statistic to compute
    """
    ss = OrderedDict()
    for key in list(mygs.keys()):
        g = mygs[key]
        tmp = np.array(())
        for n in g.nodes():
            sg = nx.ego_graph(g, n, radius=i)
            tmp = np.append(
                tmp,
                np.sum([sg.get_edge_data(e[0], e[1])["weight"] for e in sg.edges()]),
            )
        ss[key] = tmp
    return ss


def density(data, nbins=500, rng=None):
    """
    Computes density for metrics which return vectors

    Required parameters:
        data:
            - Dictionary of the vectors of data
    """
    density = OrderedDict()
    xs = OrderedDict()
    for subj in data:
        hist = np.histogram(data[subj], nbins)
        hist = np.max(hist[0])
        dens = gaussian_kde(data[subj])
        if rng is not None:
            xs[subj] = np.linspace(rng[0], rng[1], nbins)
        else:
            xs[subj] = np.linspace(0, np.max(data[subj]), nbins)
        density[subj] = dens.evaluate(xs[subj]) * np.max(data[subj] * hist)
    return {"xs": xs, "pdfs": density}


def write(outdir, metric, data, atlas):
    """
    Write computed derivative to disk in a pickle file

    Required parameters:
        outdir:
            - Path to derivative save location
        metric:
            - The value that was calculated
        data:
            - The results of this calculation
        atlas:
            - Name of atlas of interest as it appears in the directory titles
    """
    with open(op.join(outdir, atlas + "_" + metric + ".pkl"), "wb") as of:
        pickle.dump({metric: data}, of)


def main():
    """
    Argument parser and directory crawler. Takes organization and atlas
    information and produces a dictionary of file lists based on datasets
    of interest and then passes it off for processing.

    Required parameters:
        atlas:
            - Name of atlas of interest as it appears in the directory titles
        basepath:
            - Basepath for which data can be found directly inwards from
        outdir:
            - Path to derivative save location
    Optional parameters:
        fmt:
            - Determines file organization; whether graphs are stored as
              .../atlas/dataset/graphs or .../dataset/atlas/graphs. If the
              latter, use the flag.
        verb:
            - Toggles verbose output statements
    """
    parser = ArgumentParser(description="Computes Graph Metrics")
    parser.add_argument("atlas", action="store", help="atlas directory to use")
    parser.add_argument("indir", action="store", help="base directory loc")
    parser.add_argument("outdir", action="store", help="base directory loc")
    parser.add_argument(
        "-f",
        "--fmt",
        action="store_true",
        help="Formatting \
                        flag. True if bc1, False if greg's laptop.",
    )
    parser.add_argument(
        "--modality",
        help="Modality of MRI scans that \
                        are being evaluated.",
        choices=["dwi", "func"],
        default="dwi",
    )
    parser.add_argument("-v", "--verb", action="store_true", help="")
    result = parser.parse_args()

    #  Sets up directory to crawl based on the system organization you're
    #  working on. Which organizations are pretty clear by the code, methinks..
    indir = result.indir
    atlas = result.atlas
    modality = result.modality

    #  Crawls directories and creates a dictionary entry of file names for each
    #  dataset which we plan to process.
    gfmt = "_elist.csv" if modality == "dwi" else "_adj.csv"
    fs = [
        indir + "/" + fl
        for root, dirs, files in os.walk(indir)
        for fl in files
        if fl.endswith(gfmt)
    ]

    p = Popen("mkdir -p " + result.outdir, shell=True)
    #  The fun begins and now we load our graphs and process them.
    compute_metrics(fs, result.outdir, atlas, result.verb)


if __name__ == "__main__":
    main()
