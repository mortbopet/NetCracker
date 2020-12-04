import re
from src.analysis.adjacencyAnalysis import *

def x7s_bounceFilter(pj):
    """ Filters out bounce wires from what is perceived as global wires
    """
    s = pj.name

    if "FAN" in s or "BYP" in s:
            match = re.search(r"_.*_[0-9]*", s)
            if match:
                return False
            else:
                return True

    return False

def filter_pjs(pjlist, tofilter):
    return [pj for pj in pjlist if not any([special in pj.name for special in tofilter])]


def x7s_handleSpecialGlobalCases(adjpass):
        # The following two PJs are fully internal and bidirectional.
        # They are seen as belonging to both their corresponding END and
        # BEG sets, which, when doing so, completes the symmetry of the name
        # based grouping.
        sp_bidir1 = getPIPJunctionNoCreate(adjpass.sb.pos, "SR1BEG_S0")
        sp_bidir2 = getPIPJunctionNoCreate(adjpass.sb.pos, "NL1BEG_N3")
        # SR1BEG3 and NL1BEG0 are perceived as bidirectional PJs because they
        # have a feedback stub in the switchbox itadjpass. To account for this, we
        # filter these from the BIDIR set and manually add them to the out set.
        non_bidir = ["NL1BEG0", "SR1BEG3"]
        adjpass.bidirs = filter_pjs(adjpass.bidirs, non_bidir)
        non_bidir_pjs = [getPIPJunctionNoCreate(adjpass.sb.pos, name) for name in non_bidir]
        adjpass.ins += adjpass.bidirs + [sp_bidir1, sp_bidir2]
        adjpass.outs += [sp_bidir1, sp_bidir2] + non_bidir_pjs

        # The following are local feedback junctions which are not captured
        # properly by the other groups. The first to inputs are technically
        # internal junctions because they are switchbox feedbacks. Detect these
        # and add them to their respective group (BEG or END)
        for pj in adjpass.ints:
            if "BEG" in pj.name and pj not in adjpass.outs:
                adjpass.outs += [pj]
            elif "END" in pj.name and pj not in adjpass.ins:
                adjpass.ins += [pj]

def x7s_addLongWiresToAdjAnalysis(adjpass):
    for pj in adjpass.bidirs:
        if pj not in adjpass.ins:
            adjpass.ins.append(pj)
        if pj not in adjpass.outs:
            adjpass.outs.append(pj)
