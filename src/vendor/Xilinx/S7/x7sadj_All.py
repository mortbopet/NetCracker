from src.analysis.adjacencyAnalysis import *
from src.vendor.Xilinx.S7.x7s import *

from src.vendor.Xilinx.S7.x7s_filters import *
from src.vendor.Xilinx.S7.x7s_clusterings import *

class X7SAdj_All(AdjacencyAnalysis):
    def __init__(self,
            description="(Xilinx 7-Series) adjacency analysis from all PJs without applying any clustering",
            key="x7sA"):
        super().__init__(
            description=description,
            key=key
        )

        self.filterFunction = lambda pj: False
        self.clusterFunction = lambda pj, **kwargs: pj.name

    def doSpecializationFiltering(self):
        """
        x7s_handleSpecialGlobalCases(self)
        def merge(l1, l2):
            return list(set(l1) | set(l2))

        self.ins = merge(self.ins, self.bidirs)
        self.ins = merge(self.ins, self.ints)
        self.ins = merge(self.ins, self.bounces)
        self.ins += [pj for pj in self.outs if any(bfg in pj.name for bfg in ["FAN_BOUNCE", "BYP_BOUNCE", "GFAN"])]

        self.outs = merge(self.outs, self.bidirs)
        self.outs = merge(self.outs, self.ints)
        self.outs = merge(self.outs, self.bounces)

        # A bit of cleanup of null-rows and columns
        self.outs = filter_pjs(self.outs, ["LOGIC_OUTS", "GCLK", "GND_WIRE"])
        self.ins = filter_pjs(self.ins,  ["CTRL", "IMUX"])
		"""
        # Todo: Some junctions are not handled correctly in the above
        # filtering; do the safe thing and place all junctions of the SB as both
        # in's and out's (user must manually filter)
        self.outs = self.sb.PIPJunctions
        self.ins = self.sb.PIPJunctions


class X7SAdj_AllLabelled(X7SAdj_All):
    def __init__(self):
        super().__init__(
            description="(Xilinx 7-Series) adjacency analysis from all PJs while labelling PIP junctions",
            key="x7sAL"
        )
        self.clusterFunction = lambda pj, **kwargs: self.clustering(pj)

    def clustering(self, pj):
        if "IMUX" in pj.name:
            return x7s_imux_labelling(pj)
        elif "LOGIC_OUTS" in pj.name:
            return x7s_logicouts_labelling(pj)
        else:
            return x7s_wireIndexClustering(pj)

class X7SAdj_AllLabelledDirection(X7SAdj_All):
    def __init__(self):
        super().__init__(
            description="(Xilinx 7-Series) adjacency analysis from all PJs while labelling PIP junctions",
            key="x7sALLoc"
        )
        self.clusterFunction = lambda pj, **kwargs: self.clustering(pj, **kwargs)

    def clustering(self, pj, **kwargs):
        isInput = "isInput" in kwargs and kwargs["isInput"]
        if "IMUX" in pj.name:
            return x7s_imux_labelling(pj)
        elif "LOGIC_OUTS" in pj.name:
            return x7s_logicouts_labelling(pj)
        elif "BEG" in pj.name or "END" in pj.name:
            return x7s_directionClustering(pj, self.sb, isInput)
        else:
            return pj.name
