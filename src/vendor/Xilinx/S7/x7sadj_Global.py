from src.analysis.adjacencyAnalysis import *
from src.vendor.Xilinx.S7.x7s import *

from src.vendor.Xilinx.S7.x7s_filters import *
from src.vendor.Xilinx.S7.x7s_clusterings import *

class X7SAdj_Global(AdjacencyAnalysis):
    def __init__(self):
        super().__init__(
            description="(Xilinx 7-Series) Adjacency analysis from global SB inputs to global SB outputs",
            key="x7sG"
        )

        self.filterFunction = lambda pj: False
        self.clusterFunction = lambda pj, **kwargs:x7s_wireIndexClustering(pj)

    def doSpecializationFiltering(self):
        x7s_handleSpecialGlobalCases(self)
        x7s_addLongWiresToAdjAnalysis(self)

        to_ignore = ["BOUNCE", "GCLK"]
        self.ins = filter_pjs(self.ins, to_ignore)
        self.outs = filter_pjs(self.outs, to_ignore)
