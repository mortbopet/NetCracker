
from src.switchbox import *
from src.PIPJunction import *
from src.point import *
from src.logger import *

import re

def x7s_mergeswitchboxes(switchboxes):
    logHeader("Xilinx switchbox merging")
    log("validating input switchboxes...")
    """ Merges a pair of left-right switchboxes in a 7-series Xilinx fpga by
        removing all connections between the pair of switchboxes and transforming
        all PIP junctions currently loaded by adjusting the horizontal resolution
        by half (effectively removing the notion of the left-right columns).

        In this transformation, PIP junctions and their connections will be removed
        from the switchboxes.
        We therefore note that any further analysis on this merged switchbox may
        not represent the actual underlying hardware. For instance, the Fan In/Out
        analysis will no longer return correct results, given the removal of connections.
    """
    global PIPJunctions

    # Validate the switchboxes which were loaded
    if len(switchboxes) != 2:
        raise Exception("exactly 2 switchboxes must be provided when merging")

    sbl = switchboxes[0] if switchboxes[0].pos.x < switchboxes[1].pos.x else switchboxes[1]
    sbr = switchboxes[0] if switchboxes[0].pos.x > switchboxes[1].pos.x else switchboxes[1]

    if sbl.pos.x + 1 != sbr.pos.x:
        raise Exception("A left-right pair of switchboxes were not provided. Switchboxes much be adjacent in the horizontal direction.")
    log("Switchboxes valid for merging!")
    log("Merging switchboxes: " + sbl.name + ", " + sbr.name)
    filteredJunctions = set()

    # Filter the connections of pip junctions within each switchbox, which connects
    # to the paired switchbox
    def filterAdjacentConnections(sb, side):
        def filterPJ(pj, conn_pj):
            doFilter = False
            if pj.pos.y != conn_pj.pos.y:
                doFilter = False
            elif side == 'L' and conn_pj.pos.x == pj.pos.x + 1:
                doFilter = True
            elif side == 'R' and conn_pj.pos.x == pj.pos.x - 1:
                doFilter = True
            return doFilter

        PJsToRemove = []
        for pj in sb.PIPJunctions:
            for pjlist in [pj.forward_pjs, pj.backward_pjs]:
                pjlist = [
                    conn_pj for conn_pj in pjlist if not filterPJ(pj, conn_pj)]
                if len(pjlist) == 0:
                    PJsToRemove.append(pj)
                    filteredJunctions.add(pj.name + str(pj.pos))

        # Remove PJs which are filtered out
        sb.PIPJunctions = [
            pj for pj in sb.PIPJunctions if pj not in PJsToRemove]

        # Iterate through all PJs of this switchbox and remove any references
        # to the just removed pipjunctions
        for pj in sb.PIPJunctions:
            pj.forward_pjs = [c_pj for c_pj in pj.forward_pjs if c_pj not in PJsToRemove]
            pj.backward_pjs = [c_pj for c_pj in pj.backward_pjs if c_pj not in PJsToRemove]

    filterAdjacentConnections(sbl, 'L')
    filterAdjacentConnections(sbr, 'R')

    log("The following junctions were filtered away through merging:" )
    for fc in filteredJunctions:
        log(fc, end= ', ')
    log()

    modifiedPJs = {}
    # Modify all PIP junctions
    for pos, pjs in PIPJunctions.items():
        newPos = Point(pos.x, pos.y)
        for pjname, pj in pjs.items():
            # Special case: LVs in the left column are called "LV_L#".
            # When merging, we want all of the LVs to fall into the same
            # grouping. As such, remove the L suffix.
            if "LV_L" in pj.name:
                match = re.search(r"LV_L(.*)", pj.name)
                pj.name = "LV" + match.groups()[0]
            if "LVB_L" in pj.name:
                match = re.search(r"LVB_L(.*)", pj.name)
                pj.name = "LVB" + match.groups()[0]
            pj.pos.x //= 2

        newPos.x //= 2
        modifiedPJs[newPos] = pjs

    # Switch globally registerred PJs to new set
    PIPJunctions = modifiedPJs

    # Create a new switchbox with the combined set of PJs for each switchbox
    mergedSB = Switchbox()
    mergedSB.PIPJunctions = sbl.PIPJunctions + sbr.PIPJunctions
    mergedSB.name = "(" + sbl.name + " | " + sbr.name + ")"
    mergedSB.pos = sbl.pos
    mergedSB.pos.x //= 2

    log("Merging finished")
    logHeader("", level = 1)
    return mergedSB
