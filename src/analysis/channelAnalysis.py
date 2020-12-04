from src.switchbox import *
from src.point import *
from src.netcrackerformat import *
from src.sbhelper import *
from src.logger import *

from src.analysis.IOAnalysis import *
from src.analysis.analysispass import *
from src.analysis.directionAnalysis import *

# ============================== Analysis results ==============================
# ==============================================================================

CHANNEL_RESULT_FILE = "channel_analysis"

class ChannelAnalysis(AnalysisPass):
    def __init__(self):
        super().__init__(
            description="Determine horizontal and vertical channel capacity based on a representative switchbox",
            key="channel",
            depends=[INOUT_ANALYSIS_RES, DIRECTION_ANALYSIS_RES],
            produces=[]
        )

    def getBidirPairs(self, bidirs):
        """Given a set of bidirectional PIP junctions, pairs the elements of the
           set based on which junctions are connected. Fails if the set cannot
           be fully described by pairs of pip junctions (ie. we except
           junctions for both ends of a bidir wire to be present in the set).
        """
        lenDirMap = {}

        for pj in bidirs:
            ext_pjs = self.sb.getExternalPJsForPJ(pj)[0]
            if len(ext_pjs) != 1:
                raise Exception("Expected single external PJ for bidirectional wire")

            ext_pj = ext_pjs[0]
            vec = self.sb.PJPosDifference(ext_pj)
            d = vec.dir
            if vec.length not in lenDirMap:
                lenDirMap[vec.length] = {}
            if vec.dir not in lenDirMap[vec.length]:
                lenDirMap[vec.length][vec.dir] = []
            lenDirMap[vec.length][vec.dir].append(pj)

        # Flatten to pairs
        bdpairs = []
        for l, m in lenDirMap.items():
            hzpair = []
            vtpair = []

            for d, pjs in m.items():
                if d.isVertical():
                    vtpair += pjs
                elif d.isHorizontal():
                    hzpair += pjs
                else:
                    raise Exception("Non-cardinal bidirectional wire?")

            for pairlist in [hzpair, vtpair]:
                if len(pairlist) > 0:
                    if len(pairlist) != 2:
                        raise Exception("Expected pair for bidirectional wires of length " + str(l) + ", dir: " + d)
                    bdpairs.append((pairlist[0], pairlist[1]))

        return bdpairs


    def getChannelContribution(self, pj):
        """ Returns the channel contribution of an output PJs external wire in
            the vertical and horizontal channels.

            returns a 2-tuple (#hz, #vt).
        """
        ext_pj = self.sb.getExternalPJsForPJ(pj)[0][0]
        vec = self.sb.PJPosDifference(ext_pj)

        return (abs(vec.x), abs(vec.y))

    def channelDistributionAnalysis(self):
        """Analysis the distribution of wires in the hz/vt channel. Does not concern
        itself with non-cardinal wires.
        """
        analysisResult = self.sb.getAnalysisResult(DIRECTION_ANALYSIS_RES)
        rectDicts = analysisResult[DIRECTION_ANALYSIS_RES_CARDINAL_PJS]

        # Pretty print the absolute count of each rectilinear type.
        distances = sorted(list(rectDicts.values())[0].keys())
        logResult(self.sb.name, CHANNEL_RESULT_FILE, "\t\t" + '\t'.join([str(f) for f in distances]))
        for direction, distanceCounts in rectDicts.items():
            logResult(self.sb.name, CHANNEL_RESULT_FILE, direction, end='\t')
            for k in sorted(distanceCounts):
                logResult(self.sb.name, CHANNEL_RESULT_FILE, str(len(distanceCounts[k])) + "\t", end='')
            logResult(self.sb.name, CHANNEL_RESULT_FILE, )
        logResult(self.sb.name, CHANNEL_RESULT_FILE, )

        logResultHeader(self.sb.name, CHANNEL_RESULT_FILE, "Routing channel estimates (#)")
        # Pretty print the absolute count of each rectilinear type.
        distances = sorted(list(rectDicts.values())[0].keys()) + ["tot"]
        logResult(self.sb.name, CHANNEL_RESULT_FILE, "\t" + '\t'.join([str(f) for f in distances]))
        for direction, distanceCounts in rectDicts.items():
            logResult(self.sb.name, CHANNEL_RESULT_FILE, direction.name, end='\t')
            tot = 0
            for k in sorted(distanceCounts):
                v = int(len(distanceCounts[k]) * k.length)
                logResult(self.sb.name, CHANNEL_RESULT_FILE, str(v) + "\t", end='')
                tot += v
            logResult(self.sb.name, CHANNEL_RESULT_FILE, str(tot))
        logResult(self.sb.name, CHANNEL_RESULT_FILE, )

    def getChannelContributions(self, pjs):
        channelContributions = [self.getChannelContribution(pj) for pj in pjs]
        hzcnt = sum(v[0] for v in channelContributions)
        vtcnt = sum(v[1] for v in channelContributions)
        return (hzcnt, vtcnt)

    def analyseChannel(self, pjs, info = None):
        """Analysis the distribution of wires in the hz/vt channel with regards
            to the set of input pip junctions.
        """
        hzcnt, vtcnt = self.getChannelContributions(pjs)

        logResultHeader(self.sb.name, CHANNEL_RESULT_FILE, "Channel analysis" + ("(" + info + ")") if info else "")
        logResult(self.sb.name, CHANNEL_RESULT_FILE, "Vertical wires:   " + str(vtcnt))
        logResult(self.sb.name, CHANNEL_RESULT_FILE, "Horizontal wires: " + str(hzcnt))

    def analyseChannelWithStubs(self, pjs, info = None):
        """ result of analyseChannel + stub wire contributions using our chosen
            heuristic for determining stub orientation
        """

        def getStubChannelContribution(pj):
            """ Returns the channel contribution of an output PJs external wire in
                the vertical and horizontal channels.

                returns a 2-tuple (#hz, #vt).
            """
            ext_pjs = self.sb.getExternalPJsForPJ(pj)[0]

            if len(ext_pjs) > 1:
                # connection has stubs.
                # Our heuristic for stub connection is the following:
                #   The stub will be connected directly to the main end-point of
                #   the wire. This is not an optimal heuristic, but we cannot
                #   say anything about how the whole wire is actually routed as of
                #   now, so this will have to do.
                if len(ext_pjs) != 2:
                    raise Exception("Channel stub contribution asssumes that only a single stub is present")

                main_pj = ext_pjs[0]
                stub_pj = ext_pjs[1]
                vec = main_pj.pos - stub_pj.pos
                if vec.length != 1:
                    raise Exception("Stub is not adjacent to main PJ!")

                vt = 1 if vec.getDirection() == Direction.N or vec.getDirection() == Direction.S else 0
                hz = 1 if vec.getDirection() == Direction.E or vec.getDirection() == Direction.W else 0

                return (hz,vt)
            else:
                # No stubs, no channel contribution
                return(0,0)


        # Get regular channel contributions
        channelContributions = [self.getChannelContribution(pj) for pj in pjs]
        hzcnt = sum(v[0] for v in channelContributions)
        vtcnt = sum(v[1] for v in channelContributions)

        # Add stub channel contributions
        stubChannelContributions = [getStubChannelContribution(pj) for pj in pjs]
        hzcnt += sum(v[0] for v in stubChannelContributions)
        vtcnt += sum(v[1] for v in stubChannelContributions)

        logResultHeader(self.sb.name, CHANNEL_RESULT_FILE, "Channel analysis w/ stubs" + ("(" + info + ")") if info else "")
        logResult(self.sb.name, CHANNEL_RESULT_FILE, "Vertical wires:   " + str(vtcnt))
        logResult(self.sb.name, CHANNEL_RESULT_FILE, "Horizontal wires: " + str(hzcnt))

    def cardinalDistribution(self, pjs):
        hzmap = {Direction.W : {}, Direction.E : {}}
        vtmap = {Direction.N : {}, Direction.S : {}}

        hzcnt, vtcnt = self.getChannelContributions(pjs)

        for pj in pjs:
            ext_pj = self.sb.getExternalPJsForPJ(pj)[0][0]
            vec = self.sb.PJPosDifference(ext_pj)
            d = vec.getDirection()

            if d == Direction.W or d == Direction.E:
                if vec.length not in hzmap[d]:
                    hzmap[d][vec.length] = []
                hzmap[d][vec.length].append(pj)
            else:
                if vec.length not in vtmap[d]:
                    vtmap[d][vec.length] = []
                vtmap[d][vec.length].append(pj)


        for m, cnt, name in [(hzmap, hzcnt, "hz"), (vtmap, vtcnt, "vt")]:
            logResult(self.sb.name, CHANNEL_RESULT_FILE, name)
            keys = set()
            for d, innermap in m.items():
                keys = keys.union(set(innermap.keys()))

            # Pretty print the ratios of each wire type.
            keys = sorted(keys)
            logResult(self.sb.name, CHANNEL_RESULT_FILE, "\t\t" + '\t'.join([str(f) for f in keys]))
            for direction, m in m.items():
                logResult(self.sb.name, CHANNEL_RESULT_FILE, str(direction), end='\t')
                for k in keys:
                    mapvalue = len(m[k]) * k if k in m else 0
                    # logResult(self.sb.name, CHANNEL_RESULT_FILE, "{:.3f}".format(
                    #     mapvalue * 100 / cnt) + "\t", end='')
                    logResult(self.sb.name, CHANNEL_RESULT_FILE, str(mapvalue) + "\t", end='')
                logResult(self.sb.name, CHANNEL_RESULT_FILE, )
            logResult(self.sb.name, CHANNEL_RESULT_FILE, )


    def run(self, sb):
        self.sb = sb
        logResultHeader(self.sb.name, CHANNEL_RESULT_FILE, "Wires emanating from switchbox (#)")

        outs = sb.getAnalysisResult(INOUT_ANALYSIS_RES)[INOUT_ANALYSIS_OUTS] + sb.getAnalysisResult(INOUT_ANALYSIS_RES)[INOUT_ANALYSIS_BOUNCES]
        bidirs = sb.getAnalysisResult(INOUT_ANALYSIS_RES)[INOUT_ANALYSIS_BIDIRS]

        # To avoid counting a bidirectional wire twice within a channel, we only
        # pick one of the ends of a bidirectional wire to count within our
        # channel
        bidirs = [a for (a,b) in self.getBidirPairs(bidirs)]
        # Add to outs set
        outs += bidirs

        def getExtPjPosDifference(pj):
            ext_pjs = self.sb.getExternalPJsForPJ(pj)[0]
            return sb.PJPosDifference(ext_pjs[0])

        # Filter into Hz/Vt wires and diagonal wires
        hzPjs = [pj for pj in outs
            if getExtPjPosDifference(pj).dir == Direction.W or getExtPjPosDifference(pj).dir == Direction.E]
        vtPjs = [pj for pj in outs
            if getExtPjPosDifference(pj).dir == Direction.N or getExtPjPosDifference(pj).dir == Direction.S]

        otherPjs = [pj for pj in outs if pj not in hzPjs and pj not in vtPjs]

        # Cardinal channel analysis
        self.channelDistributionAnalysis()


        # 1st channel estimate: Only hz/vt wires
        self.analyseChannel(hzPjs + vtPjs, "Only hz/vt wires")
        self.cardinalDistribution(hzPjs + vtPjs)

        # 2nd channel estimate: Add non-cardinal wires
        self.analyseChannel(hzPjs + vtPjs + otherPjs, "all (without stubs)")

        # 3rd channel estimate: Add stubs
        self.analyseChannelWithStubs(hzPjs + vtPjs + otherPjs, "all (+ stubs)")
