
from src.vendor.Xilinx.UltraScale.xusadj_GlobalNoLongs import *


# ====================== Command line interface extension ======================
def addUltraScaleArguments(subparsers):
    subparser = subparsers.add_parser(name='xus', help="Xilinx UltraScale analyses")


class XilinxUltraScaleVendor():
    def __init__(self):
        # Register Xilinx UltraScale passes
        XUSAdj_GlobalNoLongs()
        return

    def getFilterPredicates(self):
        return []
    
    def postProcess(self, switchboxes, args):
        return switchboxes