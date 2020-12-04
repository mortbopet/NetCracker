from src.analysis.adjacencyAnalysis import *
from src.vendor.Xilinx.S7.x7s import *

from src.vendor.Xilinx.S7.x7s_filters import *
from src.vendor.Xilinx.S7.x7s_clusterings import *

class X7SAdj_GlobalNoLongs(AdjacencyAnalysis):
    def __init__(self,
            description="(Xilinx 7-Series) Adjacency analysis from global SB inputs to global SB outputs, disregarding long wires",
            key="x7sGNL"):
        super().__init__(
            description=description,
            key=key
        )

        self.filterFunction = lambda pj: any(lv in pj.name for lv in ["LV", "LH"])
        self.clusterFunction = lambda pj, **kwargs:x7s_wireIndexClustering(pj)

    def doSpecializationFiltering(self):
        x7s_handleSpecialGlobalCases(self)

        to_ignore = ["BOUNCE", "GCLK"]
        self.ins = filter_pjs(self.ins, to_ignore)
        self.outs = filter_pjs(self.outs, to_ignore)


class X7SAdj_GlobalNoLongsDirection(X7SAdj_GlobalNoLongs):
    def __init__(self):
        super().__init__(
            description="(Xilinx 7-Series) Adjacency analysis from global SB inputs to global SB outputs, disregarding long wires (direction clustering)",
            key="x7sGNLDir"
        )
        self.clusterFunction = lambda pj, **kwargs: x7s_directionClustering(pj, self.sb, "isInput" in kwargs and kwargs["isInput"])


class X7SAdj_GlobalNoLongsNoStubs(AdjacencyAnalysis):
    def __init__(self,
            description="(Xilinx 7-Series) Adjacency analysis from global SB inputs to global SB outputs, disregarding long wires and stubs",
            key="x7sGNLNS"):
        super().__init__(
            description=description,
            key=key
        )

        self.filterFunction = lambda pj: self.GNLNSFilter(pj)
        self.clusterFunction = lambda pj, **kwargs:x7s_wireIndexClustering(pj)

    def GNLNSFilter(self, pj):
        if any(lv in pj.name for lv in ["LV", "LH"]):
            return True

        if "BEG" in pj.name:
            return False

        match=re.search(r"^[A-Z]*[0-9]*(BEG|END)[0-9]*$", pj.name)
        return not match


    def doSpecializationFiltering(self):
        x7s_handleSpecialGlobalCases(self)

        to_ignore = ["BOUNCE", "GCLK"]
        self.ins = filter_pjs(self.ins, to_ignore)
        self.outs = filter_pjs(self.outs, to_ignore)