
def addNoVendorArguments(subparsers):
    subparser = subparsers.add_parser(name='none', help="No vendor specified")

class NoVendor():
    def getFilterPredicates(self):
        return []

    def postProcess(self, switchboxes, args):
        return switchboxes