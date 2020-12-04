import re
from src.point import *

# ============================ Clustering functions ============================



def xus_wireIndexClustering(pj):
    s = pj.name

    # Check for long wires
    match = re.search(r"^([A-Z]*[0-9]*)(_BEG|_END)[0-9]", s)
    if(match):
        return match.groups()[0] + match.groups()[1] + "#"

    # Check for local wires
    match = re.search(r"^([A-Z]*[0-9]*_([A-Z]))(_BEG|_END)[0-9]", s)
    if(match):
        return match.groups()[0] + match.groups()[1] + match.groups()[2] + "#"

    return s