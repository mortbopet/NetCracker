import sys
import os

NETCRACKER_ROOT = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..")
NETCRACKER_MAIN = os.path.join(NETCRACKER_ROOT, "netcracker.py")

sys.path.append(NETCRACKER_ROOT)

import unittest
import subprocess
from src import passmanager
from src.vendor.Xilinx.S7 import x7s

class TestPass(unittest.TestCase):
    def __init__(self, passName):
        super(TestPass, self).__init__("runNetcracker")
        self.passName = passName

    def runNetcracker(self):
        example_file = os.path.join(NETCRACKER_ROOT, "examples", "Xilinx", "7-Series", "INT_R_X15Y128_netcracker.json")
        FNULL = open(os.devnull, 'w')
        ret = subprocess.call(
            ["python3", NETCRACKER_MAIN, "-f", example_file, "-%s" % self.passName,"x7s"],
            stdout=FNULL, stderr=FNULL)
        self.assertEqual(ret, 0, "Pass '%s' returned non-zero exit code" % self.passName)


def getx7spasses():
    # @Todo: passes should register with their dependent vendor so we do not rely
    # on a string match

    # Initialize vendors to register its passes
    x7s.Xilinx7SeriesVendor()

    x7sPasses = []
    for k, p in passmanager.allPasses.items():
        if "x7" in k:
            x7sPasses.append(k)
    return x7sPasses

def x7s_testSuite():
    passes = getx7spasses()
    suite = unittest.TestSuite()
    for p in passes:
        suite.addTest(TestPass(p))

    return suite

if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(x7s_testSuite())