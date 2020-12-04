from src.analysis.adjacencyAnalysis import *
from src.vendor.Xilinx.S7.x7s import *

from src.vendor.Xilinx.S7.x7s_filters import *

""" Clusters together IMUX outputs which terminate at the same pin in the LUT
"""
class X7SAdj_LocalToLUTPin(AdjacencyAnalysis):
    def __init__(self):
        super().__init__(
            description="(Xilinx 7-Series) Clusters together local outputs which terminate at the same pin in the LUT",
            key="x7sLPin"
        )

        self.filterFunction =x7s_bounceFilter
        self.clusterFunction = lambda pj, **kwargs: self.pinClustering(pj)

    def pinClustering(self, pj):
        # Cluster switchbox inputs using wire index clustering
        if pj in self.ins:
            return x7s_wireIndexClustering(pj)

        # Internal outputs
        return x7s_imux_pincluster(pj)

    def doSpecializationFiltering(self):
        x7s_handleSpecialGlobalCases(self)
        # Make outs locals
        self.outs = [pj for pj in self.ints if "IMUX" in pj.name]
