from src.switchbox import *
from src.point import *
from src.netcrackerformat import *
from src.sbhelper import *
from src.logger import *

from src.analysis.IOAnalysis import *

from src.analysis.analysispass import *

# ============================== Analysis results ==============================

# ==============================================================================

FANIO_RESULT_FILE = "fan_io_analysis"

def groupByFunctor(objects, functor):
    groups = {}
    for obj in objects:
        key = functor(obj)
        if key not in groups:
            groups[key] = []
        groups[key].append(obj)
    return groups


class FanIOAnalysis(AnalysisPass):
    def __init__(self):
        super().__init__(
            description="Determine Fan-in/Fan-out for the PIP junctions of a switchbox",
            key="fanio",
            depends=[INOUT_ANALYSIS_RES],
            produces=[]
        )

    def run(self, sb):
        """ Groups the different classes of PJs within this switchbox based on their
            class (in, out, internal,...) and secondly based on the fan-in or
            fan-out of the PJ.
        """
        inout_res = sb.getAnalysisResult(INOUT_ANALYSIS_RES)
        ins = inout_res[INOUT_ANALYSIS_INS]
        outs = inout_res[INOUT_ANALYSIS_OUTS]
        bidir = inout_res[INOUT_ANALYSIS_BIDIRS]
        internals = inout_res[INOUT_ANALYSIS_INTS]

        # Group inputs and outputs wrt. the number of in- or outgoing PIPs
        fanOutGroups = groupByFunctor(ins, lambda pj: len(pj.forward_pjs))
        fanInGroups = groupByFunctor(outs, lambda pj: len(pj.backward_pjs))

        # Internals
        fanOutInternalGroups = groupByFunctor(
            internals, lambda pj: len(pj.forward_pjs))
        fanInInternalGroups = groupByFunctor(
            internals, lambda pj: len(pj.backward_pjs))

        logResultHeader(sb.name, FANIO_RESULT_FILE, "Fan In/Out analysis")
        logResultHeader(sb.name, FANIO_RESULT_FILE, "Fan-out of Switchbox inputs:", level=1)
        for fanCnt, PJs in fanOutGroups.items():
            logResult(sb.name, FANIO_RESULT_FILE, "Fan-out :" + str(fanCnt))
            for pj in PJs:
                logResult(sb.name, FANIO_RESULT_FILE, pj.name, end=', ')
            logResult(sb.name, FANIO_RESULT_FILE, '\n')
        logResult(sb.name, FANIO_RESULT_FILE, '\n')

        logResultHeader(sb.name, FANIO_RESULT_FILE, "Fan-in of Switchbox outputs:", level=1)
        for fanCnt, PJs in fanInGroups.items():
            logResult(sb.name, FANIO_RESULT_FILE, "Fan-in :" + str(fanCnt))
            for pj in PJs:
                logResult(sb.name, FANIO_RESULT_FILE, pj.name, end=', ')
            logResult(sb.name, FANIO_RESULT_FILE, '\n')
        logResult(sb.name, FANIO_RESULT_FILE, '\n')

        logResultHeader(sb.name, FANIO_RESULT_FILE, "Fan-out of Switchbox internal PJs:", level=1)
        for fanCnt, PJs in fanOutInternalGroups.items():
            logResult(sb.name, FANIO_RESULT_FILE, "Fan-out :" + str(fanCnt))
            for pj in PJs:
                logResult(sb.name, FANIO_RESULT_FILE, pj.name, end=', ')
            logResult(sb.name, FANIO_RESULT_FILE, '\n')
        logResult(sb.name, FANIO_RESULT_FILE, '\n')

        logResultHeader(sb.name, FANIO_RESULT_FILE, "Fan-in of Switchbox internal PJs:", level=1)
        for fanCnt, PJs in fanInInternalGroups.items():
            logResult(sb.name, FANIO_RESULT_FILE, "Fan-in :" + str(fanCnt))
            for pj in PJs:
                logResult(sb.name, FANIO_RESULT_FILE, pj.name, end=', ')
            logResult(sb.name, FANIO_RESULT_FILE, '\n')
        logResult(sb.name, FANIO_RESULT_FILE, '\n')
