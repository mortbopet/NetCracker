from src.analysis.adjacencyAnalysis import *
from src.vendor.Xilinx.S7.x7s import *

from src.vendor.Xilinx.S7.x7s_filters import *
from src.vendor.Xilinx.S7.x7s_clusterings import *

class X7SAdj_GlobalToLocal(AdjacencyAnalysis):
    def __init__(self,
            description="(Xilinx 7-Series) Adjacency analysis from global SB inputs to IMUX junctions",
            key="x7sGCLB"):
        super().__init__(
            description=description,
            key=key
        )

        self.filterFunction = lambda pj: any(lv in pj.name for lv in ["LV", "LH"])
        self.clusterFunction = lambda pj, **kwargs:self.clustering(pj)

    def clustering(self, pj):
        if "IMUX" in pj.name:
            return x7s_imux_labelling(pj)
        else:
            return x7s_wireIndexClustering(pj)

    def doSpecializationFiltering(self):
        x7s_handleSpecialGlobalCases(self)

        fan_byps = ["FAN", "BYP"]
        ins_to_ignore = ["BOUNCE", "GCLK"]
        self.ins = filter_pjs(self.ins, ins_to_ignore)
        self.outs = [pj for pj in self.ints if "IMUX" in pj.name]

class X7SAdj_GlobalToLocalDirection(X7SAdj_GlobalToLocal):
    def __init__(self,
            description="(Xilinx 7-Series) Adjacency analysis from global SB inputs to IMUX junctions (direction clustering)",
            key="x7sGCLBDir"):
        super().__init__(
            description=description,
            key=key
        )

        self.clusterFunction = lambda pj, **kwargs:self.clustering(pj, **kwargs)

    def clustering(self, pj, **kwargs):
        if "IMUX" in pj.name:
            return x7s_imux_labelling(pj)
        else:
            return x7s_directionClustering(pj, self.sb, "isInput" in kwargs and kwargs["isInput"])
