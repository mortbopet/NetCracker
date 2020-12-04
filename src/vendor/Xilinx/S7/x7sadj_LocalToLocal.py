from src.analysis.adjacencyAnalysis import *
from src.vendor.Xilinx.S7.x7s import *


class X7SAdj_LocalToLocal(AdjacencyAnalysis):
    def __init__(self):
        super().__init__(
            description="(Xilinx 7-Series) Adjacency analysis from local outputs to local inputs",
            key="x7sLL"
        )

        self.filterFunction =x7s_bounceFilter

        # No clustering
        self.clusterFunction = lambda pj, **kwargs: x7s_locals_labelling(pj)

    def doSpecializationFiltering(self):
        # Make ins and outs locals
        self.ins = [pj for pj in self.ints if "LOGIC_OUTS" in pj.name]
        self.outs = [pj for pj in self.ints if "IMUX" in pj.name]
