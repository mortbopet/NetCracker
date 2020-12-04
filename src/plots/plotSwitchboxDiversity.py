import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

import colorsys
import numpy as np
import random
import sys
import os

UNIQUE_CUTOFF = 25
LIGHTNESS = 0.6 # [0, 1]
SATURATION = 0.95 # [0, 1]
# Fraction of the Hue scale ([0, 1]) which is dedicated to non-cutoff colors.
# Cutoff switchbox types will get allocated a random color in the remainder of the scale.
PROP_TO_UNIQUE = 0.5
# Hue-scale offset (rotation) - modifies the point where most-frequent switchbox types
# are allocated from
ROTATE = 60/360


def isCutoff(cnt, uniqueCnt):
    return cnt < UNIQUE_CUTOFF and len(uniqueCnt) > UNIQUE_CUTOFF

def getUniqueValCnt(matrix):
    uniqueCnt = {}
    (rows, cols) = matrix.shape
    for row in range(rows):
        for col in range(cols):
            v = matrix[row][col]
            if v == 0:
                continue
            if v in uniqueCnt:
                uniqueCnt[v] += 1
            else:
                uniqueCnt[v] = 1
    return uniqueCnt

def createLegendData(uniqueCnt, colormap):
    legend = {}

    sortedCnt = sorted(uniqueCnt, key=lambda k: uniqueCnt[k])

    for v in sortedCnt:
        cnt = uniqueCnt[v]
        if isCutoff(cnt, uniqueCnt):
            continue
        v = int(v)
        legend[v] = (cnt, colormap[v])
    return legend


def uniqueToColors(matrix):
    """

    input:
        matrix: a 2D matrix containing values corresponding to the switchbox
        group which is present at the given index.

    Returns:
        An equivallently sized matrix as the input matrix, but with values changed
        to colors (a size 3 list of an RGB tuple) representing the switchbox type.
    """

    # UniqueCnt is a map of {switchbox type ID : count}
    uniqueCnt = getUniqueValCnt(matrix)
    N = len(uniqueCnt)
    maxCnt = max([cnt for k, cnt in uniqueCnt.items()])

    # Figure out which switchbox group IDs are over our cutoff threshold
    groupsOverCutoff = [int(v) for v, cnt in uniqueCnt.items() if not isCutoff(cnt, uniqueCnt)]
    groupsUnderCutoff = [int(v) for v, cnt in uniqueCnt.items() if int(v) not in groupsOverCutoff]
    groupsOverCutoff = sorted(groupsOverCutoff, key=lambda k: uniqueCnt[k])
    groupsOverCutoff = groupsOverCutoff[::-1]

    # We now want to be able to generate N colors evenly spaced in the hue scale
    N = len(groupsOverCutoff)
    N_under = len(groupsUnderCutoff)
    HLS_tuples = [((x*1.0/N + ROTATE) % PROP_TO_UNIQUE, LIGHTNESS, SATURATION) for x in range(N)] # Hue, lightness, saturation
    RGB_tuples = list(map(lambda x: colorsys.hls_to_rgb(*x), HLS_tuples)) # convert to RGB required for matplotlib

    HLS_tuples_under = [((x*1.0/N_under) % (1.0 - PROP_TO_UNIQUE) + PROP_TO_UNIQUE, LIGHTNESS, SATURATION) for x in range(N_under)] # Hue, lightness, saturation
    RGB_tuples_under = list(map(lambda x: colorsys.hls_to_rgb(*x), HLS_tuples_under)) # convert to RGB required for matplotlib


    # Next, we generate our color map. colorMap will be a map of
    # {switchbox type ID : [R, G, B]}
    colorMap = {}
    for v, cnt in uniqueCnt.items():
        if v in groupsOverCutoff:
            colorMap[v] = RGB_tuples[groupsOverCutoff.index(v)]
        else:
            # Group is under the cutoff limit, assign black as a color
            colorMap[v] = RGB_tuples_under[groupsUnderCutoff.index(v)]  #colorsys.hls_to_rgb((random.random() % (1.0 - PROP_TO_UNIQUE)) + PROP_TO_UNIQUE, LIGHTNESS, SATURATION) #[0, 0, 0]

    (rows, cols) = matrix.shape

    colorMatrix = np.ones(shape=(rows, cols, 3))

    # Finally, iterate over the entire input matrix and substitute colors based on
    # the seen switchbox type IDs.
    for row in range(rows):
        for col in range(cols):
            v = matrix[row][col]
            if v != 0:
                colorMatrix[row][col] = list(colorMap[v])

    return (colorMatrix, createLegendData(uniqueCnt, colorMap))

def addLegendToPlot(plt, legendmap):
    handles = []
    for v, (cnt, color) in legendmap.items():
        patch = mpatches.Patch(color=color, label=str(cnt))
        handles.append(patch)

    # Add cutoff label
    handles.append(mpatches.Patch(color='black', label="<%s" % UNIQUE_CUTOFF))
    plt.legend(handles=handles, bbox_to_anchor=(1, -0.10), ncol=4)

def plotSwitchboxDiversityMatrix(matrix, outputfolder = ''):
    matrix, legends = uniqueToColors(matrix)

    # ROTATE 90* but keep x and y axes
    matrix = np.rot90(matrix, k=1, axes=(0, 1))
    matrix = np.flip(matrix, 0)

    plt.imshow(matrix, interpolation='nearest', origin='lower')
    plt.gca().invert_yaxis()
    plt.xlabel("y")
    plt.ylabel("x")
    plt.savefig(os.path.join(outputfolder, 'switchboxcomparison.pdf'))
    plt.savefig(os.path.join(outputfolder, 'switchboxcomparison.svg'))
    # addLegendToPlot(plt, legends)
    plt.show()


if __name__ == "__main__":
    # Load a precomputed adjacency matrix file
    adjmux = np.loadtxt(sys.argv[1])
    plotSwitchboxDiversityMatrix(adjmux)