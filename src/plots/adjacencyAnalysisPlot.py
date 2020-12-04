from matplotlib.ticker import MaxNLocator
import matplotlib.pyplot as plt
import math
import numpy as np

from src.sbhelper import *
from src.netcrackerformat import *
from src.analysis.adjacencyAnalysis import *

from graphviz import *

from src.analysis.analysispass import *

class AdjacencyAnalysisPlot(AnalysisPass):
    def __init__(self):
        super().__init__(
            description="Adjacency analysis result plotting using GraphViz",
            key="plotaa",
            depends=[ADJACENCY_ANALYSIS_RES],
            produces=[]
        )

    def run(self, sb, colorFunctor = None, engine = 'fdp', filename='adjacencygraph.gv'):
        """Keyword Arguments:
        engine {str} -- String representing the graphViz engine to use (default: {'fdp'})
        filename {str} -- File to output graph to (default: {'adjacencygraph.gv'})
        colorFunctor {[type]} -- functor, given a key, returns a  (default: {None})
    """
        dot = Digraph(comment=sb.name, engine=engine)
        dot.node_attr.update(style='filled')

        adjacencyResult = sb.getAnalysisResult(ADJACENCY_ANALYSIS_RES)

        rowkeys = adjacencyResult[ADJACENCY_ANALYSIS_RES_ROWKEYS]
        colkeys = adjacencyResult[ADJACENCY_ANALYSIS_RES_COLKEYS]
        matrix = adjacencyResult[ADJACENCY_ANALYSIS_RES_MATRIX]

        # Add all keys as verticies
        for kl in [rowkeys, colkeys]:
            for k in kl:
                color = 'white'
                if colorFunctor:
                    color = colorFunctor(k)

                dot.node(k, fillcolor="%s" % color)

        for i_r, kr in enumerate(rowkeys):
            for i_c, kc in enumerate(colkeys):
                if matrix[i_r][i_c]:
                    dot.edge(kr, kc)


        dot.render(os.path.join(sbResultFolder(sb), filename), view=True)
