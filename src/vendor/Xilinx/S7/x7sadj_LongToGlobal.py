from src.analysis.adjacencyAnalysis import *
from src.vendor.Xilinx.S7.x7s import *

from src.vendor.Xilinx.S7.x7s_filters import *
from src.vendor.Xilinx.S7.x7s_clusterings import *

class X7SAdj_LongToGlobal(AdjacencyAnalysis):
    def __init__(self,
            description="(Xilinx 7-Series) Adjacency analysis from long SB inputs to global SB outputs",
            key="x7sLTG"):
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

        # Only keep long wires in SB inputs
        newIns = []
        for pj in self.ins:
            if any([special in pj.name for special in ["LV", "LH"]]):
                newIns.append(pj)

        self.ins = newIns

class X7SAdj_LongToGlobalDirection(X7SAdj_LongToGlobal):
    def __init__(self):
        super().__init__(
            description="(Xilinx 7-Series) Adjacency analysis from long SB inputs to global SB outputs (direction clustering)",
            key="x7sLTGDir"
        )
        self.clusterFunction = lambda pj, **kwargs: x7s_directionClustering(pj, self.sb, "isInput" in kwargs and kwargs["isInput"])
