from src.sbhelper import *
from src.logger import *

""" A simple pass manager which schedules all selected analysis passes and plots
    based on their dependencies.
"""
# Dictionary of pass keys : pass objects
allPasses = {}
enabledPasses = []
# A dictionary of pass result : result producer
allProducers = {}
enabledProducers = {}


def printPassInfo():
    logHeader("Pass info", echoToConsole = True)
    for p in allPasses:
        allPasses[p].printHelp()
    logHeader("", echoToConsole = True)


def addProducer(p, producerMap):
    for res in p.produces:
        producerMap[res] = p


def registerPass(k, passObj):
    if k in allPasses:
        raise Exception("Error registering pass '" + passObj.key + "': Analysis pass with key '" +
                        k + "' already registerred by pass '" + allPasses[k].key)
    allPasses[k] = passObj
    addProducer(passObj, allProducers)


def enablePass(k):
    passObj = allPasses[k]
    enabledPasses.append(passObj)

    # Ensure that no other pass produces the values of the enabled pass
    for res in passObj.produces:
        if res in enabledProducers:
            raise Exception("Producer already registerred for pass result: '"
                            + res + "'")

    addProducer(passObj, enabledProducers)


def schedulePasses():
    """ Returns a list of passes to be executed in order.
        Passes will be schedule topologically sorted based on their
        result dependencies.
    """
    def topologicalSortPasses():
        def topologicalSortUtil(p, visited, stack):
            visited[p] = True

            # Recur for all passes which produces dependencies of this pass
            for resDep in p.depends:
                if resDep not in enabledProducers:
                    # Pass was not explicitely specified. Implicitly enable the
                    # pass.
                    if resDep not in allProducers:
                        raise Exception(
                            "No pass available which produces result of name: '" + resDep + "'")
                    else:
                        depProducer = allProducers[resDep]
                        log("'%s' required by pass '%s', implicitely enabling pass '%s'." % (
                            resDep, p.key, depProducer.key))
                        enablePass(depProducer.key)
                        visited[depProducer] = False

                dependencyProducingPass = enabledProducers[resDep]
                if not visited[dependencyProducingPass]:
                    topologicalSortUtil(
                        dependencyProducingPass, visited, stack)

            # Push current pass to stack which stores result
            stack.insert(0, p)

        # Mark all passes as not visited
        visitedMap = {p: False for p in enabledPasses}
        passStack = []

        # Iterate over the visitedMap using the sorting utility function. Note
        # that we iterate over a copy of the keys instead of the items - this is due to
        # that visitedMap may change (grow) during topological sorting if we
        # implicitely enable more passes
        for p in list(visitedMap):
            if not visitedMap[p]:
                topologicalSortUtil(p, visitedMap, passStack)

        return passStack[::-1]

    return topologicalSortPasses()


################################################################################

# Register analysis passes
from src.analysis.directionAnalysis import *
from src.analysis.distributionAnalysis import *
from src.analysis.posBasedFilter import *
from src.analysis.channelAnalysis import *
from src.analysis.IOAnalysis import *
from src.analysis.fanIOAnalysis import *
from src.analysis.adjacencyAnalysis import *
from src.analysis.switchboxDiversity import *
from src.analysis.distributionAnalysis import *

ChannelAnalysis()
DirectionAnalysis()
DistributionAnalysis()
IOAnalysis()
FanIOAnalysis()
SwitchboxDiversityAnalysis()

# Register plot passes
from src.plots.adjacencyAnalysisPlot import *
from src.plots.nonCardinalWiresPlot import *
from src.plots.cardinalWiresPlot import *

AdjacencyAnalysisPlot()
NonCardinalWiresPlot()
CardinalWiresPlot()
