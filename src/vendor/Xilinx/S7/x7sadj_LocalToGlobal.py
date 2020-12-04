from src.analysis.adjacencyAnalysis import *
from src.vendor.Xilinx.S7.x7s import *

from src.vendor.Xilinx.S7.x7s_filters import *
from src.vendor.Xilinx.S7.x7s_clusterings import *

class X7SAdj_LocalToGlobal(AdjacencyAnalysis):
    def __init__(self,
            description="(Xilinx 7-Series) Adjacency analysis from local outputs to global junctions",
            key="x7sCLBG"):
        super().__init__(
            description=description,
            key=key
        )

        self.filterFunction = False
        self.clusterFunction = lambda pj, **kwargs:self.clustering(pj)

    def clustering(self, pj):
        if "LOGIC_OUTS" in pj.name:
            return x7s_logicouts_labelling(pj)
        else:
            return x7s_wireIndexClustering(pj)

    def doSpecializationFiltering(self):
        x7s_handleSpecialGlobalCases(self)

        self.ins = [pj for pj in self.ints if "LOGIC_OUTS" in pj.name]
        self.outs += [pj for pj in self.bidirs if any(lv in pj.name for lv in ["LV", "LH"])]
        self.outs = filter_pjs(self.outs, ["END", "BOUNCE"])

class X7SAdj_LocalToGlobalDirection(X7SAdj_LocalToGlobal):
    def __init__(self,
            description="(Xilinx 7-Series) Adjacency analysis from local outputs to global junctions (direction clustering)",
            key="x7sCLBGDir"):
        super().__init__(
            description=description,
            key=key
        )

        self.clusterFunction = lambda pj, **kwargs: self.clustering(pj, **kwargs)

    def clustering(self, pj, **kwargs):
        isInput = "isInput" in kwargs and kwargs["isInput"]
        if "LOGIC_OUTS" in pj.name:
            return x7s_logicouts_labelling(pj)
        else:
            return x7s_directionClustering(pj, self.sb, isInput)
