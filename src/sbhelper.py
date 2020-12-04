import json
import re
from src.point import *

# Given a map of maps ({k : {} }), analyses the keys of all submaps and returns
# a new map where all submaps contain the same keys. Nonexisting keys are
# initialized by value @param default
def addMissingKeys(mapOfMaps, default = 0):
    keys = set()

    # Gather all key variants
    for outerKey, innerMap in mapOfMaps.items():
        keys = keys.union(innerMap.keys())

    # Add missing keys in each map
    for outerKey, innerMap in mapOfMaps.items():
        for k in keys:
            if k not in mapOfMaps[outerKey]:
                mapOfMaps[outerKey][k] = default

    return mapOfMaps

def extractDictsToList(dicts):
    ldicts = []
    for k, v in dicts.items():
        ldicts.append({k : v})
    return ldicts

def parseWirelengthData(datafile):
    icMap = {}
    with open(datafile) as file:
        inmap = json.load(file)
        for ic, data in inmap.items():
            outmap = {}
            for k, v in data.items():
                x = re.search(r"x=(-?[0-9]*)", k).groups()[0]
                y = re.search(r"y=(-?[0-9]*)", k).groups()[0]
                outmap[Point(x,y)] = v
            icMap[ic] = outmap

    return icMap
