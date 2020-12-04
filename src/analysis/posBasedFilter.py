from src.switchbox import *
from src.point import *
from src.netcrackerformat import *

# ============================== Analysis results ==============================
FILTER_GLOBAL_RES = "global pjs"        # Type: [PIPJunction]
FILTER_LOCAL_RES = "local pjs"          # Type: [PIPJunction]
FILTER_INTERNAL_RES = "internal pjs"    # Type: [PIPJunction]
# ==============================================================================


def posBasedFilter(sb):
    globalPJs = []
    localPJs = []
    internalPJs = []
    for pj in sb.PIPJunctions:
        connectsToGlobal = False
        connectsToLocal = False
        connectsToInternal = False
        for pjlist in [pj.forward_pjs, pj.backward_pjs]:
            for c_pj in pjlist:
                posDifference = c_pj.pos - pj.pos
                if posDifference.length == 0:
                    connectsToInternal = True
                elif posDifference.length == 1:
                    connectsToLocal = True
                elif posDifference.length > 1:
                    connectsToGlobal = True

        if connectsToInternal:
            internalPJs.append(pj)
        if connectsToLocal:
            localPJs.append(pj)
        if connectsToGlobal:
            globalPJs.append(pj)

    sb.results[FILTER_GLOBAL_RES] = globalPJs
    sb.results[FILTER_LOCAL_RES] = localPJs
    sb.results[FILTER_INTERNAL_RES] = internalPJs
