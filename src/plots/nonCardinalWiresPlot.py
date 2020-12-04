from matplotlib.ticker import MaxNLocator
import matplotlib.pyplot as plt
import math
import numpy as np

from src.sbhelper import *
from src.netcrackerformat import *
from src.analysis.directionAnalysis import *

from src.analysis.analysispass import *

class NonCardinalWiresPlot(AnalysisPass):
    def __init__(self):
        super().__init__(
            description="Non-cardinal wire plotting",
            key="plotnoncardinal",
            depends=[DIRECTION_ANALYSIS_RES],
            produces=[]
        )

    def run(self, sb, showTitle = False):
        fig, ax = plt.subplots(subplot_kw=dict(polar=True))
        maxY = 0.0

        # Move radial labels to the horizontal line
        ax.set_rlabel_position(0)

        title = sb.name
        diagdict = sb.getAnalysisResult(DIRECTION_ANALYSIS_RES)[DIRECTION_ANALYSIS_RES_NON_CARDINAL_PJS]


        kw = dict(arrowstyle="<-",color='black', linestyle="-", fill=False)
        for direction, vectors in diagdict.items():
            for vector, PJs in vectors.items():
                # This is a bit of a workaround:
                #   ax.annotate with an arrow + text draws an arrow towards the text. It
                #   is the text which will be placed in the xytext position, and the arrow
                #   will terminate "somewhere" neat the text.
                #   However, we would like the arrow to precisely terminate at the specified
                #   position. So we create two separate annotations; one for the arrow,
                #   one for the text.
                kwi = kw.copy()
                kwi.update(dict(linewidth=1))#dataForIc[v]))
                ax.annotate('', xytext=(vector.angle, vector.length), xy=(0,0), arrowprops=kwi)

                # Text draws towards the right. If we are in the 2nd or 3rd quadrant,
                # slightly adjust the text position to account for this
                r = vector.length
                a = vector.angle
                if vector.dir == "NW" or vector.dir == "SW":
                    r = np.hypot(vector.x - 0.4, vector.y)
                    a = np.arctan2(vector.y, vector.x - 0.4)
                ax.annotate(str(len(PJs)),xytext=(a, r), xy=(0,0))

                # Update maximum Y range
                maxY = np.maximum(np.max(vector.length), maxY)

        ax.set_ylim(0, maxY*1.1)
        ax.set_xticklabels(["E", "NE", "N", "NW", "W", "SW", "S", "SE"])
        ax.yaxis.set_major_locator(MaxNLocator(integer=True)) # force integer y axis

        if showTitle:
            plt.title(title)

        #plt.ylabel('Hops')
        plt.show()