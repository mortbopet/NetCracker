from src.point import *
from enum import Enum


# Map of all PIP Junctions instantiated in the current analysis
# { tile (Point) : {PIP Junction name : PIPJunction}}
PIPJunctions = {}

def resetPIPJunctions():
    """ Removes all registerred PIP junctions. Calls to getPIPJunction will
        return new PIP junctions. Use cautiously!
    """
    PIPJunctions.clear()

def registerPipJunction(pj):
    if not pj.pos in PIPJunctions:
        PIPJunctions[pj.pos] = {}

    if pj.name in PIPJunctions[pj.pos]:
        raise Exception("PIP Junction already registered!")

    PIPJunctions[pj.pos][pj.name] = pj


def getPIPJunction(pos, name):
    """ Returns the PIP junction corresponding to the given POS and name. If the PIP
        Junction does not exist, the PIP junction is created and registered
    """
    if type(pos) is not Point:
        raise Exception("Position is not specified as a point")

    if pos in PIPJunctions:
        if name in PIPJunctions[pos]:
            return PIPJunctions[pos][name]
    PIPJunction(pos, name)
    return getPIPJunction(pos, name)

def getPIPJunctionNoCreate(pos, name):
    """ Returns the PIP junction corresponding to the given POS and name. If the PIP
        Junction does not exist, an exception is thrown.
    """
    if type(pos) is not Point:
        raise Exception("Position is not specified as a point")

    if pos in PIPJunctions:
        if name in PIPJunctions[pos]:
            return PIPJunctions[pos][name]
    raise Exception("Unknown PIP junction")


class PIPJunction:
    def __init__(self, pos, name):
        self.name = name
        self.pos = pos
        registerPipJunction(self)

        # List of PIP Junctions which may be driven by this PIP junction
        self.forward_pjs = []
        # List of PIP Junctions which may drive this PIP junction
        self.backward_pjs = []

    def __eq__(self, other):
        return self.pos == other.pos and self.name == other.name

    def __hash__(self):
        return hash((self.pos, self.name))

    def __str__(self):
        return "[ " + self.name + str(self.pos) + "]"

    def addPJ(self, pjlist, pj):
        pjlist.append(pj)

    def addForwardPJ(self, pj):
        self.addPJ(self.forward_pjs, pj)

    def addBackwardPJ(self, pj):
        self.addPJ(self.backward_pjs, pj)

    def isBidirectional(self):
        return len(self.forward_pjs) > 1 and len(self.backward_pjs) > 1
