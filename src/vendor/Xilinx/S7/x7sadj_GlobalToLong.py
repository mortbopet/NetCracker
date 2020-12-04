from src.analysis.adjacencyAnalysis import *
from src.vendor.Xilinx.S7.x7s import *

from src.vendor.Xilinx.S7.x7s_filters import *
from src.vendor.Xilinx.S7.x7s_clusterings import *

class X7SAdj_GlobalToLong(AdjacencyAnalysis):
    def __init__(self,
            description="(Xilinx 7-Series) Adjacency analysis from global SB inputs to long SB outputs",
            key = "x7sGTL"):
        super().__init__(
            description=description,
            key=key
        )

        self.filterFunction = lambda pj: False
        self.clusterFunction = lambda pj, **kwargs:x7s_wireIndexClustering(pj)

    def doSpecializationFiltering(self):
        x7s_handleSpecialGlobalCases(self)
        x7s_addLongWiresToAdjAnalysis(self)

        to_ignore = ["BOUNCE", "GCLK"]
        self.ins = filter_pjs(self.ins, to_ignore)
        self.outs = filter_pjs(self.outs, to_ignore)

        # Only keep long wires in SB outputs
        newOuts = []
        for pj in self.outs:
            if any([special in pj.name for special in ["LV", "LH"]]):
                newOuts.append(pj)

        self.outs = newOuts

class X7SAdj_GlobalToLongDirection(X7SAdj_GlobalToLong):
    def __init__(self):
        super().__init__(
            description="(Xilinx 7-Series) Adjacency analysis from global SB inputs to long SB outputs (direction clustering)",
            key="x7sGTLDir"
        )
        self.clusterFunction = lambda pj, **kwargs: x7s_directionClustering(pj, self.sb, "isInput" in kwargs and kwargs["isInput"])
