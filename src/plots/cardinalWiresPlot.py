from matplotlib.ticker import MaxNLocator
import matplotlib.pyplot as plt
import math
import numpy as np

from src.sbhelper import *
from src.netcrackerformat import *
from src.analysis.directionAnalysis import *

class CardinalWiresPlot(AnalysisPass):
    def __init__(self):
        super().__init__(
            description="Cardinal wire plotting",
            key="plotcardinal",
            depends=[DIRECTION_ANALYSIS_RES],
            produces=[]
        )

    def run(self, sb):
        # dirData is a map of {direction : { hops : count }}
        dirData = {}
        for d in filter(lambda d: d.isCardinal(), Direction):
            dirData[d] = {}

        rectidict = sb.getAnalysisResult(DIRECTION_ANALYSIS_RES)[DIRECTION_ANALYSIS_RES_CARDINAL_PJS]

        # 1. Sum rectilinear direction data of switchbox
        for direction, points in rectidict.items():
            for vector, PJs in points.items():
                dirData[direction][vector.length] = len(PJs)

        # 2. Each direction must have an equal number of keys for the plot.
        #    Fill out missing keys with zeros

        # Get the largest hop distance
        dMax = -1
        for direction, v in dirData.items():
            thisMax = max(v)
            if thisMax > dMax:
                dMax = thisMax
        dMax = int(math.ceil(dMax))

        # Add missing keys for each direction
        for direction, v in dirData.items():
            for i in range(1, dMax + 1):
                if i not in dirData[direction]:
                    dirData[direction][i] = 0

        # Now we may plot the data
        x = np.arange(dMax)
        width = 0.2  # the width of the bars
        fig, ax = plt.subplots()
        for di, (direction, data) in enumerate(dirData.items()):
            values = []

            # We need values in sorted order
            for i in range (1, dMax + 1):
                values.append(data[i])

            offset = width/2 + (di*width -(len(dirData)*width / 2))

            ax.bar(x + offset, values, width, label=direction)

        # Add some text for labels, title and custom x-axis tick labels, etc.
        ax.yaxis.set_major_locator(MaxNLocator(integer=True))
        ax.set_ylabel('# Wires', fontsize=14)
        ax.set_xlabel('Hops', fontsize=14)
        ax.set_title(sb.name + ' Wires per hop distance')
        ax.set_xticks(x)
        ax.set_xticklabels(x + 1)
        ax.legend()
        plt.tight_layout()
        plt.show()