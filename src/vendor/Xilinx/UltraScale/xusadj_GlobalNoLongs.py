from src.analysis.adjacencyAnalysis import *

from src.vendor.Xilinx.UltraScale.xus_filters import *
from src.vendor.Xilinx.UltraScale.xus_clusterings import *

class XUSAdj_GlobalNoLongs(AdjacencyAnalysis):
    def __init__(self,
            description="(Xilinx UltraScale) Adjacency analysis from global SB inputs to global SB outputs, disregarding long wires",
            key="xusGNL"):
        super().__init__(
            description=description,
            key=key
        )

        self.filterFunction = lambda pj: any(lv in pj.name for lv in ["BOUNCE", "GCLK", "LOGIC_OUTS", "IMUX", "CTRL", "BYPASS"])
        self.clusterFunction = lambda pj, **kwargs:xus_wireIndexClustering(pj)

    def doSpecializationFiltering(self):
        self.ins += self.ints
        self.outs += self.ints
        return