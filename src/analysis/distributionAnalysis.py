from src.switchbox import *
from src.point import *
from src.netcrackerformat import *
from src.sbhelper import *
from src.logger import *

from src.analysis.directionAnalysis import *

from src.analysis.analysispass import *

# ============================== Analysis results ==============================

# ==============================================================================

DISTRIBUTION_RESULT_FILE = "distribution_analysis"

class DistributionAnalysis(AnalysisPass):
    def __init__(self):
        super().__init__(
            description="Determine the distribution of wire types within each channel",
            key="distribution",
            depends=[DIRECTION_ANALYSIS_RES],
            produces=[]
        )

    def run(self, sb):
        logResultHeader(sb.name, DISTRIBUTION_RESULT_FILE, "directional wire distribution (%)")

        analysisResult = sb.getAnalysisResult(DIRECTION_ANALYSIS_RES)
        diagDicts = analysisResult[DIRECTION_ANALYSIS_RES_DIAG_CNT]
        rectDicts = analysisResult[DIRECTION_ANALYSIS_RES_RECT_CNT]

        # Count total number of wires
        wirecount = 0
        for dirDict in [diagDicts, rectDicts]:
            for direction, distanceCounts in dirDict.items():
                wirecount += sum(distanceCounts.values())

        # Pretty print the ratios of each diagonal type.
        # For labels, we want to illustrate the square base
        distances = sorted(list(diagDicts.values())[0].keys())
        distances = [round(math.sqrt(math.pow(f, 2) / 2)) for f in distances]
        logResult(sb.name, DISTRIBUTION_RESULT_FILE, "\t" + '\t'.join([str(f) for f in distances]))
        for direction, distanceCounts in diagDicts.items():
            logResult(sb.name, DISTRIBUTION_RESULT_FILE, direction, end='\t')
            for k in sorted(distanceCounts):
                logResult(sb.name, DISTRIBUTION_RESULT_FILE, "{:.3f}".format(
                    distanceCounts[k] * 100 / wirecount) + "\t", end='')
            logResult(sb.name, DISTRIBUTION_RESULT_FILE, )
        logResult(sb.name, DISTRIBUTION_RESULT_FILE, )

        # Pretty print the ratios of each rectilinear type.
        distances = sorted(list(rectDicts.values())[0].keys())
        logResult(sb.name, DISTRIBUTION_RESULT_FILE, "\t" + '\t'.join([str(f) for f in distances]))
        for direction, distanceCounts in rectDicts.items():
            logResult(sb.name, DISTRIBUTION_RESULT_FILE, direction, end='\t')
            for k in sorted(distanceCounts):
                logResult(sb.name, DISTRIBUTION_RESULT_FILE, "{:.3f}".format(
                    distanceCounts[k] * 100 / wirecount) + "\t", end='')
            logResult(sb.name, DISTRIBUTION_RESULT_FILE, )
        logResult(sb.name, DISTRIBUTION_RESULT_FILE, )
