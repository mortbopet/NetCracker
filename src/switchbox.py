import numpy as np
import math
from enum import Enum
import sys

from src.sbhelper import *
from src.point import *
from src.netcrackerformat import *
from src.PIPJunction import *
from src.logger import *

class PJClassification(Enum):
    """An enum may be classified with respect to a switchbox. The result of such
    classification is returned as the following enum.
    """
    IN = 1          # The PJ is driven by an external PJ
    OUT = 2         # The PJ drives an external PJ
    EXTERNAL = 3    # The PJ is not in the switchbox
    INTERNAL = 4    # The PJ drives and is drive by PJs internal to the switchbox
    BOUNCE = 5      # The PJ drives internal PJs but may bounce (drive) an external PJ aswell
    BIDIR = 6       # The PJ is in the switchbox but is bidirectional


class Switchbox:
    def __init__(self, name, data=None, namePredicates=None):
        """Constructs a switchbox based on input in Nutcracker format.

            namePredicates:
                List of functors <bool(str)> which, if evaluated to true, will
                exclude a PIP Junction from being included in this switchbox.
        """

        # Switchbox data fields
        self.data = data
        self.name = name
        self.pos = None
        self.options = None
        self.PIPJunctions = []

        # Analysis results
        # Results are stored as a map. Analysis should define their own analysis
        # name which is then the key for retreiving the result of the given
        # analysis.
        self.results = {}

        if data is not None:
            # Initialize switchbox from data
            self.initialize(namePredicates)

    def initialize(self, namePredicates):
        """Initializes this switchbox based on the input data

        Arguments:
            namePredicates: List of functors for filtering PJ names. If functor
            evaluates to true, the PJ will be disregarded.
        """
        def pjIsFiltered(pjname):
            for namePredicate in namePredicates:
                if namePredicate(pjname):
                    return True
            return False

        def tryLoadVariable(d, vname, optional = False):
            try:
                return d[vname]
            except:
                if not optional:
                    log("Error: Could not load variable '" + vname +
                        "' from switchbox data (switchbox: '" + self.name + "')")
                    sys.exit(1)

        self.pos = Point(
            x=tryLoadVariable(self.data, NETCRACKER_SB_POS_X),
            y=tryLoadVariable(self.data, NETCRACKER_SB_POS_Y))
        self.options = tryLoadVariable(self.data, NETCRACKER_SB_OPTS, optional=True)

        for pj in tryLoadVariable(self.data, NETCRACKER_SB_PJS):
            pjName = tryLoadVariable(pj, NETCRACKER_PJ_NAME)
            if pjIsFiltered(pjName):
                continue

            pjForwardPjs = tryLoadVariable(pj, NETCRACKER_PJ_FW_PJS)
            pjBackwardPjs = tryLoadVariable(pj, NETCRACKER_PJ_BK_PJS)

            # Construct PJ. Ensure that they dont reference the same point object
            pjObj = getPIPJunction(Point(x=self.pos.x, y=self.pos.y), pjName)

            # Initialzie the PIP Junctions referenced by pj
            for f_pj in pjForwardPjs:
                f_pjName = tryLoadVariable(f_pj, NETCRACKER_PJ_NAME)
                if pjIsFiltered(f_pjName):
                    continue
                f_pjPos = Point(
                    x=tryLoadVariable(f_pj, NETCRACKER_PJ_POS_X),
                    y=tryLoadVariable(f_pj, NETCRACKER_PJ_POS_Y))
                pjObj.addForwardPJ(getPIPJunction(f_pjPos, f_pjName))

            for b_pj in pjBackwardPjs:
                b_pjName = tryLoadVariable(b_pj, NETCRACKER_PJ_NAME)
                if pjIsFiltered(b_pjName):
                    continue
                b_pjPos = Point(
                    x=tryLoadVariable(b_pj, NETCRACKER_SB_POS_X),
                    y=tryLoadVariable(b_pj, NETCRACKER_SB_POS_Y))
                pjObj.addBackwardPJ(getPIPJunction(b_pjPos, b_pjName))

            # Add the PJ to the PJs of this switchbox
            if pjObj in self.PIPJunctions:
                raise Exception("PJ Already added to this switchbox!")
            self.PIPJunctions.append(pjObj)

    def getAnalysisResult(self, analysisname):
        if analysisname not in self.results:
            raise Exception("Analysis '" + analysisname +
                            "' was not found. Has the analysis been run?")
        return self.results[analysisname]

    def PJPosDifference(self, pj):
        """Returns a point of the difference in position between @p pj and this
        switchbox.
        """
        return pj.pos - self.pos

    def getExternalPJsForPJ(self, pj):
        """Given a @p pj, returns two lists containing all of the connected
        PJs of @p pj which are not in this switchbox """
        if pj not in self.PIPJunctions:
            raise Exception(
                "Can only get external PJs for PJs within the switchbox")

        extOuts = [
            c_pj for c_pj in pj.forward_pjs if c_pj not in self.PIPJunctions]
        extIns = [
            c_pj for c_pj in pj.backward_pjs if c_pj not in self.PIPJunctions]

        # Sanity checking: We cannot have both external ins and external outs
        if extOuts and extIns:
            raise Exception(
                "We cannot have both external ins and external outs of a PJ")

        return extOuts, extIns

    def classifyPJ(self, pj):
        """Given a @p PJ within this switchbox, tries to classify whether the PJ
           is an input to the switchbox (driven by the global routing network)
           or an output (drives the routing network).

           A PJ is an input if its forward PJs are within the switchbox.
           A PJ is an output if its forward PJs are external to the switchbox.
        """

        # Is the PJ in this switchbox?
        if pj not in self.PIPJunctions:
            return PJClassification.EXTERNAL

        allInsInSB = all(inPJ.pos == self.pos for inPJ in pj.backward_pjs)
        allOutsInSB = all(outPJ.pos == self.pos for outPJ in pj.forward_pjs)
        allInsNotInSB = all(inPJ.pos != self.pos for inPJ in pj.backward_pjs)
        allOutsNotInSB = all(outPJ.pos != self.pos for outPJ in pj.forward_pjs)
        anyOutNotInSB = any(outPJ.pos != self.pos for outPJ in pj.forward_pjs)

        if allInsInSB and allOutsInSB:
            return PJClassification.INTERNAL

        if allOutsNotInSB:
            return PJClassification.OUT

        if allInsNotInSB:
            return PJClassification.IN

        if len(pj.backward_pjs) > 1 and len(pj.forward_pjs) > 1:
            return PJClassification.BIDIR

        if allInsInSB and anyOutNotInSB:
            return PJClassification.BOUNCE

        raise Exception("Could not classify PJ")

    def dump(self):
        """Dumps information about this switchbox
        """
        logHeader("Switchbox dump")
        log("Name:\t" + self.name)
        log("Pos:\t" + str(self.pos))
        log("Options:\t" + str(self.options))
        log("PIP Junctions:\t")
        for pj in self.PIPJunctions:
            log(pj.name)
        log()
