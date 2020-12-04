from src.analysis.adjacencyAnalysis import *
from src.vendor.Xilinx.S7.x7s import *

from src.vendor.Xilinx.S7.x7s_filters import *
from src.vendor.Xilinx.S7.x7s_clusterings import *

class X7SAdj_GlobalLocalToGlobalLocal(AdjacencyAnalysis):
    def __init__(self,
            description="(Xilinx 7-Series) Adjacency analysis from global and local SB inputs to global and local SB outputs",
            key="x7sGLGL"):
        super().__init__(
            description=description,
            key=key
        )

        self.filterFunction = lambda pj: any(lv in pj.name for lv in ["LV", "LH"])
        self.clusterFunction = lambda pj, **kwargs:self.clustering(pj)

    def clustering(self, pj):
        if "IMUX" in pj.name or "LOGIC_OUTS" in pj.name:
            return pj.name # do not lable these; may connect to unlableable PJs
        else:
            return x7s_wireIndexClustering(pj)

    def doSpecializationFiltering(self):
        x7s_handleSpecialGlobalCases(self)

        fan_byps = ["FAN", "BYP"]
        to_ignore = ["BOUNCE", "GCLK"]
        self.ins = filter_pjs(self.ins, to_ignore)
        self.ins += [pj for pj in self.ints if "LOGIC_OUTS" in pj.name]
        self.outs += [pj for pj in self.ints if "IMUX" in pj.name]
