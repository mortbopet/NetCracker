from src.analysis.adjacencyAnalysis import *
from src.vendor.Xilinx.S7.x7s import *

from src.vendor.Xilinx.S7.x7s_filters import *
from src.vendor.Xilinx.S7.x7s_clusterings import *

class X7SAdj_GlobalToBFG(AdjacencyAnalysis):
    def __init__(self,
            description="(Xilinx 7-Series) Adjacency analysis from global SB inputs to FAN, BYP and GFAN junctions",
            key="x7sGBFG"):
        super().__init__(
            description=description,
            key=key
        )

        self.filterFunction = lambda pj: any(lv in pj.name for lv in ["LV", "LH"])
        self.clusterFunction = lambda pj, **kwargs:x7s_wireIndexClustering(pj)

    def doSpecializationFiltering(self):
        x7s_handleSpecialGlobalCases(self)

        fan_byps = ["FAN", "BYP"]
        to_ignore = ["BOUNCE", "GCLK"]
        self.ins = filter_pjs(self.ins, to_ignore)
        self.outs += [pj for pj in self.bounces if any(bfg in pj.name for bfg in fan_byps)]
        self.outs += [pj for pj in self.ints if any(bfg in pj.name for bfg in fan_byps)]
        self.outs = [pj for pj in self.outs if any(bfg in pj.name for bfg in fan_byps)]


class X7SAdj_GlobalToBFGDirection(X7SAdj_GlobalToBFG):
    def __init__(self,
            description="(Xilinx 7-Series) Adjacency analysis from global SB inputs to FAN, BYP and GFAN junctions (direction clustering)",
            key="x7sGBFGDir"):
        super().__init__(
            description=description,
            key=key
        )

        self.clusterFunction = lambda pj, **kwargs: x7s_directionClustering(pj, self.sb, "isInput" in kwargs and kwargs["isInput"])
