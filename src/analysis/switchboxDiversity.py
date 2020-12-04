from src.switchbox import *
from src.point import *
from src.netcrackerformat import *
from src.sbhelper import *
from src.direction import *

from src.analysis.adjacencyAnalysis import *
from src.plots.plotSwitchboxDiversity import *

DIVERSITY_ANALYSIS_RESULT_FILE = "switchbox_diversity"

def getAdjacencyTypesMatrix(w, h, sbAdjacencyTypes):
    N = len(sbAdjacencyTypes)
    matrix = np.zeros(shape=(h + 1,w + 1))

    sortedSbs = sorted(sbAdjacencyTypes, key=lambda k: len(sbAdjacencyTypes[k]))

    for k in sortedSbs:
        for sb in sbAdjacencyTypes[k]:
            v = matrix[sb.pos.y][sb.pos.x]
            matrix[sb.pos.y][sb.pos.x] = N
        N -= 1

    return matrix

def matrix2dhash(matrix):
    innerhashes = [tuple(x) for x in matrix]
    return hash(tuple(innerhashes))

def AAResultToNPMatrix(aares):
    # Given an adjacency analysis result (consisting of row and column keys + an
    # adjacency matrix), inserts keys into the matrix and returns a single 2d
    # matrix
    arr = aares["matrix"]

    # Add column headers. Also helps to initially mix the datatypes of the array
    # for further numpy manipulation
    arr = [aares["colkeys"]] + arr


    arr = np.array(arr)
    rowkeys = ["-"] + aares["rowkeys"]
    arr = np.insert(arr, 0, rowkeys, 1)

    # deterministically sort first on column keys, then on row keys
    arr = arr[:, np.argsort(arr[0])] # sort on column keys
    arr = arr[np.argsort(arr[:, 0])] # sort on row keys

    return arr


class SwitchboxDiversityAnalysis(AnalysisPass):
    def __init__(self):
        super().__init__(
            description="Determine the distribution of different switchbox types across the device, based on the results of any adjacency analysis",
            key="sbdiversity",
            depends=[ADJACENCY_ANALYSIS_RES],
            produces=[],
            executesOnAllSBs=True
        )

    def run(self, sbs):
        """ Compares a set of switchboxes based on whether they have similar adjacency analysis results
            as well as set of PIP junctions.
            The comparison is performed as follows:

            For each switchbox:
                1. Get adjacency analysis results
                2. Sort adjacency analysis results such that row and column order is
                deterministic
                3. resulting matrix is hashed
                4. if hash already exists => identical adjacency else
                5. record hash as newly recorded adjacency result, along with a
                reference to the switchbox.
        """
        dim = None

        # ========================== Adjacency comparison ==========================
        # We maintain a mapping of switchbox matricies and references to the
        # switchboxes which exhibit identical connectivity to that matrix
        sbAdjacencyTypes = {}
        # A mapping of adjacency results with equal dimensions
        sbDimTypes = {}

        for sb in sbs:
            aares = sb.getAnalysisResult(ADJACENCY_ANALYSIS_RES)
            thisdim = (len(aares["matrix"]), len(aares["matrix"][0]))
            """
            if dim is None:
                dim = thisdim
            else:
                if dim != thisdim:
                    raise Exception("Unequal adjacency matrix dimensions")
            """
            matrix = AAResultToNPMatrix(aares)
            mkey = matrix2dhash(matrix)
            if mkey not in sbAdjacencyTypes:
                sbAdjacencyTypes[mkey] = [sb]
            else:
                sbAdjacencyTypes[mkey].append(sb)

            if thisdim not in sbDimTypes:
                sbDimTypes[thisdim] = [sb]
            else:
                sbDimTypes[thisdim].append(sb)

        # Todo: Now, we take a look at the different kind of switchbox types
        # and see how they actually differ - is it in the keys? is it in the values?

        # todo: need a good way to convey the dimensions of the FPGA
        adjmux = getAdjacencyTypesMatrix(43, 149 ,sbAdjacencyTypes)
        np.savetxt(os.path.join(OUTPUT_FOLDER, DIVERSITY_ANALYSIS_RESULT_FILE + '.txt'), adjmux)
        plotSwitchboxDiversityMatrix(adjmux, outputfolder=OUTPUT_FOLDER)


        # ========================= PIP Junction comparison ========================
        # We maintain a mapping of a set of PIP junction names within a switchbox,
        # and references to switchboxes which contain these.
        sbPJTypes = {}
        for sb in sbs:
            pjs = tuple(sorted([pj.name for pj in sb.PIPJunctions]))
            if pjs not in sbPJTypes:
                sbPJTypes[pjs] = [sb]
            else:
                sbPJTypes[pjs].append(sb)

        return
