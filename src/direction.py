from enum import Enum

class Direction(Enum):
    N = 1
    S = 2
    E = 3
    W = 4
    NE = 5
    NW = 6
    SE = 7
    SW = 8
    INVALID = 9

    def isCardinal(self):
        return self in [Direction.N, Direction.S, Direction.E, Direction.W]

    def isOrdinal(self):
        return self in [Direction.NW, Direction.SW, Direction.SE, Direction.NE]

    def isVertical(self):
        return self in [Direction.N, Direction.S]

    def isHorizontal(self):
        return self in [Direction.E, Direction.W]
