import argparse
import json
import re
import pprint
import sys

import numpy as np
import matplotlib.pyplot as plt

from src.sbhelper import *
from src.analysis.IOAnalysis import *
from src.analysis.analysispass import *
from src.logger import *


# ============================== Analysis results ==============================
"""type:
    {
        'rowKeys' : [string],
        'colKeys' : [string],
        'matrix' : [[int]]
    }
"""
ADJACENCY_ANALYSIS_RES = "Adjacency analysis result"
ADJACENCY_ANALYSIS_RES_ROWKEYS = 'rowkeys'
ADJACENCY_ANALYSIS_RES_COLKEYS = 'colkeys'
ADJACENCY_ANALYSIS_RES_MATRIX  = 'matrix'

# ==============================================================================

ADJACENCY_ANALYSIS_RESULT_FILE = "adjacency_analysis"

def plotAdjacencyMatrix(adjm, xkeys, ykeys):
    fig, ax = plt.subplots()
    im = ax.imshow(adjm)
    ax.set_xticks(np.arange(len(xkeys)))
    ax.set_yticks(np.arange(len(ykeys)))
    ax.set_xticklabels(xkeys)
    ax.set_yticklabels(ykeys)

    # Rotate the tick labels and set their alignment.
    plt.setp(ax.get_xticklabels(), rotation=90, ha="right",
            rotation_mode="anchor")
    plt.show()


def adjMatrixFromXYLists(vx, vy, adjListAccessFunctor):
    disregardedConns = set()
    disregardedConnsCnt = 0
    matrix = []
    for k in vy:
        innerMatrix = [0] * len(vx)
        for adjKey in vy[k]:
            try:
                i = list(vx.keys()).index(adjKey)
                innerMatrix[i] += 1
            except ValueError:
                # adjacent key was not considered for this analysis.
                # In the context of PJs, may happen if ie. we are doing adjacency
                # internally in the switchbox using forward PJs, but the given PJ
                # has a forward PJ externally to the switchbox (drives the global
                # routing network).
                disregardedConns.add(adjKey)
                disregardedConnsCnt += 1
                continue

        matrix.append(innerMatrix)

    logHeader("Disregarded %s connections to PJs:" %
                (str(disregardedConnsCnt)), level=1)
    for c in disregardedConns:
        log(c, end=', ')
    log()

    return matrix

def singleToList(obj):
    return obj if type(obj) is list else [obj]

class AdjacencyAnalysis(AnalysisPass):
    def __init__(self, description, key):
        super().__init__(
            description=description,
            key=key,
            depends=[INOUT_ANALYSIS_RES],
            produces=[ADJACENCY_ANALYSIS_RES]
        )

        self.sb = None

        """
        self.clusterFunction is a lambda for specifying the clustering specific
        to this adjacency analysis pass. Should be set by the implementing analysis.
            Args:
                pj ([PIPJunction]): PIP junction to cluster
            Args [optional]: All optional arguments provided as **kwarg dict
                isInput ([Boolean]): true if the PIP junction is an input to this switchbox
        """        
        self.clusterFunction = None

    def doSpecializationFiltering(self):
        raise Exception("Adjacency analysis specialization must implement this")

    def dumpAdjacencyMatrix(self, adjm, xkeys, ykeys):
        fn = ADJACENCY_ANALYSIS_RESULT_FILE + "_" + self.key
        # Write column labels
        for k in xkeys:
            logResult(self.sb.name, fn, "\t" + k, end = '')
        logResult(self.sb.name, fn)
        # Write rows
        for i, row in enumerate(adjm):
            logResult(self.sb.name, fn, ykeys[i], end = '')
            for v in row:
                logResult(self.sb.name, fn, '\t' + str(v), end = '')
            logResult(self.sb.name, fn)
        logResult(self.sb.name, fn)


    def run(self, sb, doPlot=False):
        """ This analysis will generate the adjacency between inputs to the switchbox
            and outputs of the switchbox. Y labels are inputs, X labels are outputs
        """
        self.sb = sb
        self.ins = sb.getAnalysisResult(INOUT_ANALYSIS_RES)[INOUT_ANALYSIS_INS]
        self.ints = sb.getAnalysisResult(INOUT_ANALYSIS_RES)[INOUT_ANALYSIS_INTS]
        self.outs = sb.getAnalysisResult(INOUT_ANALYSIS_RES)[INOUT_ANALYSIS_OUTS]
        self.bidirs = sb.getAnalysisResult(INOUT_ANALYSIS_RES)[INOUT_ANALYSIS_BIDIRS]
        self.bounces = sb.getAnalysisResult(INOUT_ANALYSIS_RES)[INOUT_ANALYSIS_BOUNCES]

        # Assert that the specialization has provided any required functions
        if self.clusterFunction == None:
            raise Exception("No cluster function set")
        if self.filterFunction == None:
            raise Exception("No filter function set")

        # Call specialization defined filtering/PJ list merging
        self.doSpecializationFiltering()

        def applyClustering(pjs, isInput = False):
            clustering = {}
            clustersize = {}
            # Applies the clustering function to the PJ itself and all of its forward
            # PJs

            clusteredPJsRev = {}
            for _pj in pjs:
                if self.filterFunction and self.filterFunction(_pj):
                    continue

                clusteredPJs = singleToList(self.clusterFunction(_pj, isInput=isInput))
                
                clusteredForwardsLists = [singleToList(self.clusterFunction(
                    fpj)) for fpj in _pj.forward_pjs]

                for clusteredPJ in clusteredPJs:
                    if clusteredPJ not in clustering:
                        clustering[clusteredPJ] = []

                    if clusteredPJ not in clustersize:
                        clustersize[clusteredPJ] = 0

                    for clusteredForwards in clusteredForwardsLists:
                        clustering[clusteredPJ] += clusteredForwards
                    clustersize[clusteredPJ] += 1

                    # Add to debug map
                    if clusteredPJ not in clusteredPJsRev:
                        clusteredPJsRev[clusteredPJ] = []
                    clusteredPJsRev[clusteredPJ].append(_pj)

            return clustering, clustersize, clusteredPJsRev

        # Transform in's and out's based on the requested clustering
        ins, insclustersize, insDebugMap = applyClustering(self.ins, isInput=True)
        outs, outsclustersize, outsDebugMap = applyClustering(self.outs)

        for name, m in [("ins", insDebugMap), ("outs", outsDebugMap)]:
            log("Group contents: " + name)
            for k, v in m.items():
                log(str(k)+": ", end = '')
                for pj in v:
                    log(pj.name + ", ", end='')
                log()
            log()


        inkeys = ['[' + str(insclustersize[k] if k in insclustersize else 1) + ']-' + str(k) for k in list(ins.keys())]
        outkeys = ['[' + str(outsclustersize[k] if k in outsclustersize else 1) + ']-' + str(k) for k in list(outs.keys())]

        # Adjacency matrix of forward PJs
        adjmatrix = adjMatrixFromXYLists(outs, ins, lambda v: ins[v])

        self.dumpAdjacencyMatrix(adjmatrix, outkeys, inkeys)

        if doPlot:
            plotAdjacencyMatrix(adjmatrix, outkeys, inkeys)

        sb.results[ADJACENCY_ANALYSIS_RES] = {
            ADJACENCY_ANALYSIS_RES_ROWKEYS : inkeys,
            ADJACENCY_ANALYSIS_RES_COLKEYS : outkeys,
            ADJACENCY_ANALYSIS_RES_MATRIX  : adjmatrix
        }
