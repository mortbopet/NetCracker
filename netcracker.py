import argparse
import progressbar

from src.sbhelper import *
from src.point import *
from src.switchbox import *
from src.passmanager import *
from src.logger import *

import json

from src.vendor.Xilinx.S7.x7s import *
from src.vendor.NoVendor.novendor import *

if __name__ == "__main__":
    logHeader("NetCracker Switchbox Analysis", echoToConsole=True)

    # Initialize vendors to register their command line arguments
    xilVendor = Xilinx7SeriesVendor()
    noVendor = NoVendor()

    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file', help='NetCracker data file')
    parser.add_argument('--passinfo', help='Show dependency information for all passes', action="store_true")

    # Add vendor-specific command line options. A user must select which vendor
    # the device to be analysed is from, given that some basic filtering will
    # be applied based on the vendor.
    vendorSubparsers = parser.add_subparsers(dest='Device vendor')
    vendorSubparsers.required = True
    addXilinxArguments(vendorSubparsers)
    addNoVendorArguments(vendorSubparsers)


    # Setup pass arguments
    for k, p in allPasses.items():
        parser.add_argument('-%s' % k, help=p.description, action="store_true")

    args = parser.parse_args()

    # Setup vendor object
    if vars(args)['Device vendor'] == 'x7s':
        vendor = xilVendor
    else:
        vendor = noVendor

    if args.passinfo:
        printPassInfo()
        sys.exit(0)

    # Enable selected passes
    for k, p in allPasses.items():
        if vars(args)[k]:
           enablePass(k)

    # Parse netcracker file
    if args.file is None:
        log("error: the following arguments are required: -f/--file", echoToConsole=True)
        sys.exit(1)

    netcrackerData = {}
    with open(args.file) as file:
        netcrackerData = json.load(file)

    # Load switchboxes
    log("Loading switchboxes...", echoToConsole=True )
    sbs = []
    for sbname, sbdata in progressbar.progressbar(netcrackerData.items()):
        sbs.append(Switchbox(sbname, sbdata, namePredicates=vendor.getFilterPredicates()))

    # Apply any vendor-specific post-processing to the switchboxes
    sbs = vendor.postProcess(sbs, args)

    # Schedule enabled passes
    execlist = schedulePasses()

    logHeader("Passes to be executed (in order):", level = 1, echoToConsole=True)
    for i, p in enumerate(execlist):
        log(str(i+1) + ":\t (" + p.key + ") " + p.description, echoToConsole=True)

    # Execute!
    logHeader("Executing single-switchbox passes...", level = 1, echoToConsole=True)
    for sb in progressbar.progressbar(sbs, redirect_stdout=True):
        log("Analysing switchbox: '%s'" % sb.name, echoToConsole=True)
        for p in execlist:
            if p.executesOnAllSBs:
                continue
            logHeader("Running pass: '%s'..." % p.key, level=1, echoToConsole=True)
            p.run(sb)
    log(echoToConsole=True)
    logHeader("Executing all-switchbox passes...", level = 1, echoToConsole=True)
    for p in progressbar.progressbar(execlist, redirect_stdout=True):
        if p.executesOnAllSBs:
            logHeader("Running pass: '%s'..." % p.key, level=1, echoToConsole=True)
            p.run(sbs)

    logHeader("Done", echoToConsole=True)
