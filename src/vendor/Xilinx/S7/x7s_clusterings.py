import re
from src.point import *

# ============================ Clustering functions ============================


def x7s_directionClustering(pj, sb, inv=False):
    """ Clusters a pip junction based on the difference vector between its external
    termination point and the reference switchbox.


    Args:
        pj ([PIPJunction]): PIP junction in @p sb
        sb ([Switchbox]): Refernce switchbox
        inv ([bool]): If true, inverts the calculated difference vector

    Returns:
        [string]: String representation of the direction vector "(dx, dy)"
    """    

    specials =  ["SR1END_N3_3", "NL1END_S3_0", "SR1BEG3", "NL1BEG0"]
    """ Clusters the PJ based on it's difference vector between itself and the
        switchbox
    """
    #pjLst = pj.backward_pjs if len(pj.backward_pjs) == 1 else pj.forward_pjs

    if any(special in pj.name for special in ["ALT", "BYP", "BOUNCE", "FAN", "IMUX", "LOGIC_OUT"]):
        if "IMUX" in pj.name:
            return x7s_imux_labelling(pj)
        if "LOGIC_OUT" in pj.name:
            return x7s_logicouts_labelling(pj)

        return pj.name

    extOuts = [
        c_pj for c_pj in pj.forward_pjs if c_pj not in sb.PIPJunctions]
    extIns = [
        c_pj for c_pj in pj.backward_pjs if c_pj not in sb.PIPJunctions]

    extlst = extOuts if len(extOuts) != 0 else extIns

    if pj.name in specials:
        extlst = pj.forward_pjs if "BEG" in pj.name else pj.backward_pjs

    groups = set()

    for extpj in extlst:
        vec = sb.PJPosDifference(extpj)
        if inv:
            vec = -vec

        if vec == Point(0,0) and pj.name not in specials:
            groups.add("INTERNAL")
        else:
            groups.add(str(vec))


    return list(groups)


def x7s_wireIndexClustering(pj):
    """ Clusters the PJ based on the wire index of the PJ wrt. its type.
        Does not group long wires

        Examples:
            NN2BEG1 -> NN2BEG#
            SW6END3 -> SW6END#
    """
    s = pj.name

    if s.startswith("LV") or s.startswith("LH"):
        # Remove side-specific naming
        s = s.replace("_L",'')
        return s

    if s.startswith("IMUX"):
        return "IMUX#"

    if s.startswith("LOGIC_OUTS"):
        return "LOGIC_OUTS#"


    # Special case: NL1BEG_N3 and SR1BEG_S0 are counted in both the input and
    # output set of the name
    if pj.name == "NL1BEG_N3":
        return ["N1END#", "N1BEG#"]

    if pj.name == "SR1BEG_S0":
        return ["S1END#", "S1BEG#"]

    # Check for local wires
    match = re.search(r"^([A-Z])[LR]([0-9]+[A-Z]*)([0-9]+|_[A-Z][0-9])", s)
    if(match):
        return match.groups()[0] + match.groups()[1] + "#"

    match = re.search(r"^([A-Z]*[0-9]+[A-Z]*)([0-9]+|_[A-Z][0-9])", s)
    if(match):
        s = match.groups()[0] + "#"
    return s


def x7s_wireDirectionLengthClustering(pj):
    """ Clusters the PJ based on the direction and length of the wire.
        Examples:
            NN2BEG1 -> NN2
            SW6END3 -> SW6
    """

    s = pj.name

    if s.startswith("LV") or s.startswith("LH"):
        return s

    match = re.search(r"([A-Z]*[0-9]+)(BEG|END)", s)
    if(match):
        s = match.groups()[0]
    return s


def x7s_wireDirectionClustering(pj):
    """ Clusters the PJ based on the direction and length of the wire.
        Examples:
            NN2BEG1 -> NN
            SW6END3 -> SW
            LVB12 -> LV
    """

    s = pj.name

    # If PJ starts with one of the following names, we may simply group on that
    predefGroups = ["LV", "LH", "IMUX", "LOGIC_OUTS"]
    for pdg in predefGroups:
        if s.startswith(pdg):
            return pdg

    match = re.search(r"([A-Z]*)[0-9]+(BEG|END)", s)
    if(match):
        s = match.groups()[0]
    return s

# Clusters IMUX wires based on which LUT they connect to in a CLB
def x7s_imux_lutcluster(pj):
    if "IMUX" in pj.name:
        # Classify IMUXes based on their connectivity to the CLB
        clbpj = pj.forward_pjs[0]
        match = re.search(r"^CLB[A-Z]*_([A-Z]*)_([A-Z])([0-9])", clbpj.name)
        if(match):
            if match.groups()[0] in ["M", "LL"] :
                idx = "T" # South lut
            else:
                idx = "U" # North lut
            lut = match.groups()[1]
            name = "IMUX_[%s:%s]" % (idx, lut)
            return name
    else:
        return pj.name

# Clusters IMUX wires based on which pin they connect to in a LUT
def x7s_imux_pincluster(pj):
    if "IMUX" in pj.name:
        # Classify IMUXes based on their connectivity to the CLB
        clbpj = pj.forward_pjs[0]
        match = re.search(r"^CLB[A-Z]*_([A-Z]*)_([A-Z])([0-9])", clbpj.name)
        if(match):
            if match.groups()[0] in ["M", "LL"]:
                idx = "T" # South lut
            else:
                idx = "U" # North lut
            pin = match.groups()[2]
            name = "IMUX_[%s:%s]" % (idx, pin)
            return name
    else:
        return pj.name

# Does not cluster IMUX wires but labels them based on which pin they connect to in a LUT
def x7s_imux_labelling(pj):
    if "IMUX" in pj.name:
        if len(pj.forward_pjs) == 0:
            return "IMUX_UNCONNECTED"

        # Classify IMUXes based on their connectivity to the CLB
        clbpj = pj.forward_pjs[0]
        match = re.search(r"^CLB[A-Z]*_([A-Z]*)_([A-Z])([0-9])", clbpj.name)
        if(match):
            if match.groups()[0] in ["M", "LL"]:
                idx = "T" # South lut
            else:
                idx = "U" # North lut
            lut = match.groups()[1]
            pin = match.groups()[2]
            name = "%s:%s%s" % (idx, lut, pin)
            return name
    else:
        return pj.name

# Clusters LOGIC_OUTS wires based on which LUT they emanate from in a CLB
def x7s_logicouts_lutcluster(pj):
    if "LOGIC_OUTS" in pj.name:
        clbpj = pj.backward_pjs[0]
        match = re.search(r"^CLB[A-Z]*_([A-Z]*)_([A-Z])([A-Z]*)", clbpj.name)
        if(match):
            if match.groups()[0] in ["M", "LL"]:
                idx = "T" # South lut
            else:
                idx = "U" # North lut
            lut = match.groups()[1]
            name = "LOGIC_OUTS_[%s:%s]" % (idx, lut)
            return name
    else:
        return pj.name

# Does not cluster together LOGIC_OUTS but labels them wrt. which LUT and LUT
# output they originate from
def x7s_logicouts_labelling(pj):
    if "LOGIC_OUTS" in pj.name:
        clbpj = pj.backward_pjs[0]
        match = re.search(r"^CLB[A-Z]*_([A-Z]*)_([A-Z])([A-Z]*)", clbpj.name)
        if(match):
            if match.groups()[0] in ["M", "LL"]:
                idx = "T" # South lut
            else:
                idx = "U" # North lut
            lut = match.groups()[1]
            pin = match.groups()[2]
            outname = lut
            if pin:
                outname += pin
            name = "%s:%s" % (idx, outname)
            return name
    else:
        return pj.name

def x7s_locals_labelling(pj):
    if "IMUX" in pj.name:
        return x7s_imux_labelling(pj)
    elif "LOGIC_OUTS" in pj.name:
        return x7s_logicouts_labelling(pj)
    else:
        return pj.name