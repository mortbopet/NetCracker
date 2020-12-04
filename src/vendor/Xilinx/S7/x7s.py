import re
from src.vendor.Xilinx.S7.x7s_mergeswitchboxes import *
from src.vendor.Xilinx.S7.x7sadj_All import *
from src.vendor.Xilinx.S7.x7sadj_LocalToLUT import *
from src.vendor.Xilinx.S7.x7sadj_LocalToLUTPin import *
from src.vendor.Xilinx.S7.x7sadj_Global import *
from src.vendor.Xilinx.S7.x7sadj_GlobalNoLongs import *
from src.vendor.Xilinx.S7.x7sadj_LocalToLocal import *
from src.vendor.Xilinx.S7.x7sadj_LongToGlobal import *
from src.vendor.Xilinx.S7.x7sadj_GlobalToLong import *
from src.vendor.Xilinx.S7.x7sadj_GlobalToBFG import *
from src.vendor.Xilinx.S7.x7sadj_LocalToBFG import *
from src.vendor.Xilinx.S7.x7sadj_GlobalToLocal import *
from src.vendor.Xilinx.S7.x7sadj_BFGToLocal import *
from src.vendor.Xilinx.S7.x7sadj_LocalToGlobal import *
from src.vendor.Xilinx.S7.x7sadj_GlobalLocalToGlobalLocal import *


# ========================= NetCracker special options =========================
NETCRACKER_X7_OPT_SIDE = "side"

# ====================== Command line interface extension ======================
def addXilinxArguments(subparsers):
    subparser = subparsers.add_parser(name='x7s', help="Xilinx 7-Series analyses")
    subparser.add_argument(
        "--merge", help="Merges two adjacent switchboxes."
        "The input data file must contain two adjacent switchbox."
        "If this is not the case, analysis will fail.",
        action='store_true')

# =========================== PIP loading predicates ===========================
# Predicate for filtering VCC/GND wires
def x7s_filterElec(PJName):
    return "VCC" in PJName or "GND" in PJName


# Predicate for filtering CLK wires
def x7s_filterClk(PJName):
    return "CLK" in PJName

# Predicate for filtering CTRL wires


def x7s_filterCtrl(PJName):
    return "CTRL" in PJName

class Xilinx7SeriesVendor():
    def __init__(self):
        # Register Xilinx passes
        X7SAdj_LocalToLocal()
        X7SAdj_Global()
        X7SAdj_LocalToLUT()
        X7SAdj_LocalToLUTPin()
        X7SAdj_All()

        X7SAdj_GlobalNoLongs()
        X7SAdj_GlobalNoLongsDirection()
        X7SAdj_GlobalNoLongsNoStubs()

        X7SAdj_LongToGlobal()
        X7SAdj_LongToGlobalDirection()

        X7SAdj_GlobalToLong()
        X7SAdj_GlobalToLongDirection()

        X7SAdj_GlobalToBFG()
        X7SAdj_GlobalToBFGDirection()

        X7SAdj_LocalToBFG()

        X7SAdj_GlobalToLocal()
        X7SAdj_GlobalToLocalDirection()

        X7SAdj_AllLabelled()
        X7SAdj_AllLabelledDirection()

        X7SAdj_BFGToLocal()

        X7SAdj_LocalToGlobal()
        X7SAdj_LocalToGlobalDirection()

        X7SAdj_GlobalLocalToGlobalLocal()

    def getFilterPredicates(self):
        return [] # [x7_filterElec,x7s_filterClk]

    def postProcess(self, switchboxes, args):
        if args.merge and args.merge == True:
            mergedSB =x7s_mergeswitchboxes(switchboxes)
            switchboxes = [mergedSB]

        return switchboxes



def x7s_wireDirectionClustering_colorfunctor(clustername):
    """ A color generator for the above clustering. Used when executing the adjacency
    graph plotting function
    """
    longwires = ["LV", "LH"]
    localWires = ['WR', 'WL', 'SR', 'SL', 'NR', 'NL', 'ER', 'EL']

    if clustername in longwires:
        return "#FFF2CC"
    if clustername in localWires:
        return "#D5E8D4"
    else:
        return "#DAE8FC"
