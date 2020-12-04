from src.switchbox import *
from src.point import *
from src.netcrackerformat import *
from src.sbhelper import *
from src.logger import *
from src.logger import *

from src.analysis.analysispass import *

# ============================== Analysis results ==============================
INOUT_ANALYSIS_RES = "IO Analysis result"     # Type: map of the following lists
INOUT_ANALYSIS_INS = "IO Analysis ins"        # Type: [PIPJunction]
INOUT_ANALYSIS_OUTS = "IO Analysis outs"      # Type: [PIPJunction]
INOUT_ANALYSIS_EXTS = "IO Analysis externals" # Type: [PIPJunction]
INOUT_ANALYSIS_BIDIRS = "IO Analysis bidirs"  # Type: [PIPJunction]
INOUT_ANALYSIS_BOUNCES = "IO Analysis bounces"# Type: [PIPJunction]
INOUT_ANALYSIS_INTS = "IO Analysis internals" # Type: [PIPJunction]
# ==============================================================================

IO_ANALYSIS_RESULT_FILE = "io_analysis"

class IOAnalysis(AnalysisPass):
    def __init__(self):
        super().__init__(
            description="Determine the in- and output PIP junctions of a switchbox",
            key="io",
            depends=[],
            produces=[INOUT_ANALYSIS_RES]
        )

    def run(self, sb, debug=True):
        """ Attempts to classify all PJs within the switchbox as either inputs,
            outputs or external PJs.
        """
        ins = []
        outs = []
        exts = []
        bidir = []
        ints = []
        bounces = []

        for pj in sb.PIPJunctions:
            c = sb.classifyPJ(pj)

            if c == PJClassification.EXTERNAL:
                exts.append(pj)
            elif c == PJClassification.IN:
                ins.append(pj)
            elif c == PJClassification.OUT:
                outs.append(pj)
            elif c == PJClassification.BIDIR:
                bidir.append(pj)
            elif c == PJClassification.INTERNAL:
                ints.append(pj)
            elif c == PJClassification.BOUNCE:
                bounces.append(pj)
            else:
                raise Exception("Could not classify PJ")

        # Write analysis results
        sb.results[INOUT_ANALYSIS_RES] = {}
        sb.results[INOUT_ANALYSIS_RES][INOUT_ANALYSIS_INS] = ins
        sb.results[INOUT_ANALYSIS_RES][INOUT_ANALYSIS_OUTS] = outs
        sb.results[INOUT_ANALYSIS_RES][INOUT_ANALYSIS_EXTS] = exts
        sb.results[INOUT_ANALYSIS_RES][INOUT_ANALYSIS_BIDIRS] = bidir
        sb.results[INOUT_ANALYSIS_RES][INOUT_ANALYSIS_INTS] = ints
        sb.results[INOUT_ANALYSIS_RES][INOUT_ANALYSIS_BOUNCES] = bounces


        if debug:
            logHeader("In/Out analysis debug output")
            def debPrint(type, pjs):
                log(type + ":")
                for pj in pjs:
                    log(pj.name, end=', ')
                log('\n')

            pjlist = [("Ins", ins), ("Outs", outs),
                    ("Exts", exts), ("Bidirs", bidir), ("Ints", ints), ("Bounces", bounces)]

            for t, pjs in pjlist:
                debPrint(t, pjs)
