from src.sbhelper import *
from src.passmanager import registerPass
from src.logger import *

""" Base class for all analysis passes
"""


class AnalysisPass:
    passes = {}

    def __init__(self, description, key, depends, produces, executesOnAllSBs = False):
        self.description = description
        self.key = key

        self.depends = depends
        self.produces = produces

        # Determines the execution policy of the pass. If set, the pass expects
        # an arbitrary number of switchboxes per run. If not set, the pass
        # expects a single switchbox per run.
        self.executesOnAllSBs = executesOnAllSBs

        registerPass(key, self)

    def run(self, sb):
        raise Exception("Unimplemented")

    def logHeader(self, text, level=0):
        logHeader(self.description + ": " + text, level)

    def printHelp(self):
        logHeader("(-" + self.key + ")", level = 1, echoToConsole = True)
        log("Description: " + self.description, echoToConsole = True)
        log("Depends on:", echoToConsole = True)
        for dep in self.depends:
            log("\t" + dep, echoToConsole = True)

        log("Produces:", echoToConsole = True)
        for res in self.produces:
            log("\t" + res, echoToConsole = True)
        log(echoToConsole = True)
