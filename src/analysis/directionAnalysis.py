from src.switchbox import *
from src.point import *
from src.netcrackerformat import *
from src.sbhelper import *
from src.direction import *
from src.logger import *

from src.analysis.posBasedFilter import *

from src.analysis.analysispass import *
from src.analysis.directionAnalysis import *

# ============================== Analysis results ==============================
DIRECTION_ANALYSIS_RES = "direction analysis"       # Type: map containing the below results as keys
DIRECTION_ANALYSIS_RES_CARDINAL_PJS = "cardinal PJs"   # Type: {Direction : {Point : [PIPJunction]}}
DIRECTION_ANALYSIS_RES_NON_CARDINAL_PJS = "non-cardinal PJs"      # Type: {Direction : {Point : [PIPJunction]}}
# ==============================================================================

DIRECTION_RESULT_FILE = "direction_analysis"

class DirectionAnalysis(AnalysisPass):
    def __init__(self):
        super().__init__(
            description="Determine source and sink location of in/out PIP junctions of a switchbox",
            key="direction",
            depends=[],
            produces=[DIRECTION_ANALYSIS_RES]
        )

    def run(self, sb, debug=True):
        dirPJs = {}

        for d in Direction:
            dirPJs[d] = {}

        for pj in sb.PIPJunctions:
            extOuts, extIns = sb.getExternalPJsForPJ(pj)

            if len(extOuts) == 0: # and len(extIns) == 0:
                continue

            extListToConsider = extOuts if extOuts else extIns

            # Consider the PJ which is furthest away
            externalPJ = None
            for extPjToConsider in extListToConsider:
                if externalPJ is None:
                    externalPJ = extPjToConsider
                else:
                    if sb.PJPosDifference(externalPJ).length < sb.PJPosDifference(extPjToConsider).length:
                        externalPJ = extPjToConsider


            # Get the direction of the vector between this switchbox and the external PJ
            extVector = sb.PJPosDifference(externalPJ)
            posDifference = sb.PJPosDifference(externalPJ)

            if posDifference not in dirPJs[extVector.dir]:
                dirPJs[extVector.dir][posDifference] = []

            dirPJs[extVector.dir][posDifference].append(pj)

        # Create dictionaries for the wire counts of diagonal and rectilinear  wires
        cardinalPJDicts = {k: v for k, v in dirPJs.items() if k.isCardinal()}
        nonCardinalPJDicts = {k: v for k, v in dirPJs.items() if not k.isCardinal()}

        # Record analysis results
        sb.results[DIRECTION_ANALYSIS_RES] = {}
        sb.results[DIRECTION_ANALYSIS_RES][DIRECTION_ANALYSIS_RES_CARDINAL_PJS] = cardinalPJDicts
        sb.results[DIRECTION_ANALYSIS_RES][DIRECTION_ANALYSIS_RES_NON_CARDINAL_PJS] = nonCardinalPJDicts

        if(debug):
            # Do debug printing
            logResult(sb.name, DIRECTION_RESULT_FILE, "Global Direction Analysis debug output")
            for k, v in dirPJs.items():
                logResult(sb.name, DIRECTION_RESULT_FILE, "Direction: " + k.name)
                for distance, pjs in v.items():
                    logResult(sb.name, DIRECTION_RESULT_FILE, str(distance) + ":")
                    for pj in pjs:
                        logResult(sb.name, DIRECTION_RESULT_FILE, pj.name, end=', ')
                    logResult(sb.name, DIRECTION_RESULT_FILE, "\n")
